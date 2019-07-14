import csv
import json

import matplotlib.backends.backend_pdf as p
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import mpld3
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
from matplotlib import pyplot
from mpld3 import plugins
from mpld3 import utils
from urllib3.connectionpool import xrange

from adminapp.models import *


class ClickInfo(plugins.PluginBase):
    """Plugin for getting info on click"""

    JAVASCRIPT = """
    mpld3.register_plugin("clickinfo", ClickInfo);
    ClickInfo.prototype = Object.create(mpld3.Plugin.prototype);
    ClickInfo.prototype.constructor = ClickInfo;
    ClickInfo.prototype.requiredProps = ["id"];
    function ClickInfo(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    ClickInfo.prototype.draw = function(){
        var obj = mpld3.get_element(this.props.id);
        obj.elements().on("mousedown", function(d, i){
        if (!clicked) {
        url = window.location.href;
        var pathArray = window.location.pathname.split('/');
        if (pathArray.length == 5) {  
            newUrl = url + "/obj=" + i;
            clicked = true; 
        }
        else {
            newUrl = url.replace("/" + pathArray[5], "/obj=" + i)
            clicked = true;
        }
        document.location.href = newUrl;
        }
        });
    }
    """

    def __init__(self, points):
        self.dict_ = {"type": "clickinfo",
                      "id": utils.get_id(points)}


class Visualizer:

    def get_classifer_visualization(self, iteration_id, subspace_id, selected_obj, *args):



        fig, ax = plt.subplots()

        iteration = Iteration.objects.get(id=iteration_id)
        setup = iteration.session_id.setup_id
        subspace_order = 0
        subspaces = Subspace.objects.filter(setup_id_id=setup.id).order_by('id')
        features = []
        dataset_type = setup.dataset_id.type

        # find subspace order manually
        for ss in subspaces:
            if ss.id != int(subspace_id):
                subspace_order += 1
            else:
                break

        # this will be used in "feature_data_visible == no", filtering the visible data
        for ss in subspaces:
            if dataset_type == "HIPE":
                if not ss.feature_x_id in features:
                    features.append(ss.feature_x_id)
                if not ss.feature_y_id in features:
                    features.append(ss.feature_y_id)
            elif dataset_type == "MNIST":
                if not (ss.feature_x_id - 1) in features:
                    features.append((ss.feature_x_id - 1))
                if not (ss.feature_y_id - 1) in features:
                    features.append((ss.feature_y_id - 1))

        if dataset_type == 'HIPE':
            feature_x_id = subspaces[subspace_order].feature_x_id
            feature_y_id = subspaces[subspace_order].feature_y_id

        elif dataset_type == 'MNIST':
            feature_x_id = subspaces[subspace_order].feature_x_id - 1
            feature_y_id = subspaces[subspace_order].feature_y_id - 1

        feature_file = setup.dataset_id.feature_file.path
        ocal_output = iteration.ocal_output
        dict = json.loads(ocal_output)
        subspace_gridpoints_all = json.loads(setup.subspaces_gridpoints_JSON)

        labels = dict["prediction_subspaces"][subspace_order]

        xy = []
        x = []
        y = []
        timestamps = []

        with open(feature_file) as f:

            plots = csv.reader(f, delimiter=',')
            headers = next(plots)

            # get the x and y values for the graph
            for row in plots:
                timestamps.append(row[0])
                x.append(float(row[feature_x_id]))
                y.append(float(row[feature_y_id]))
                xy.append(row)

        # add some padding for a nicer view
        paddingX = (max(x) - min(x)) / 10
        paddingY = (max(y) - min(y)) / 10

        plt.xlim(min(x) - paddingX, max(x) + paddingX)
        plt.ylim(min(y) - paddingY, max(y) + paddingY)

        # bring the points in (x,y) form
        objects = np.column_stack((x, y))
        w = list(objects)

        # bring the points to a valid for for scatter()
        points = np.array(w).astype("float")

        label_values = np.array([])
        counter = 0
        ocal_selection_exists = False

        # coloring the inliers and outliers
        for label in labels:
            value = -1
            if counter == selected_obj:
                value = 2  # the query-id to be questioned
            elif counter == args[0] and setup.feedback_mode == "hybrid":
                value = 3 # OCAL-Selection
                ocal_selection_exists = True
            elif label == "inlier":
                value = 1
            elif label == "outlier":
                value = 0
            label_values = np.append(label_values, value)
            counter += 1

        label_color = ['green' if i == 0 else 'blue' if i == 1 else 'yellow' if i == 3 else 'red' for i in label_values]

        red_patch = mpatches.Patch(color='red', label='Selection')
        blue_patch = mpatches.Patch(color='blue', label='Inlier')
        green_patch = mpatches.Patch(color='green', label='Outlier')

        if ocal_selection_exists and setup.feedback_mode == "hybrid":
            yellow_patch = mpatches.Patch(color='yellow', label='OCAL Selection')
            plt.legend(handles=[blue_patch, green_patch, red_patch, yellow_patch])
        else:
            plt.legend(handles=[blue_patch, green_patch, red_patch])

        scatter = plt.scatter(points[:, 0], points[:, 1], c=label_color)

        all_subspace_gridpoints = subspace_gridpoints_all["visualization"]
        subspace_gridpoints = all_subspace_gridpoints[subspace_order]

        # create gridpoints
        xx, yy = np.meshgrid(subspace_gridpoints[0],
                             subspace_gridpoints[1])

        # Put the result into a color plot
        # bring the scores to a valid form for contour()
        Z = np.array(dict["score_subspace_grids"][subspace_order])
        Z[Z > 0] = 1
        Z[Z <= 0] = 0
        Z = Z.reshape(xx.shape)
        plt.contour(xx, yy, Z, cmap=plt.cm.Paired)

        # plot the grid
        plt.grid(linestyle='dotted')


        # plot the labels
        xlabel = plt.xlabel(headers[feature_x_id], fontsize=22)
        ylabel = plt.ylabel(headers[feature_y_id], fontsize=22)

        df = pd.read_csv(feature_file, sep=',', skiprows=0, header=0)
        tooltip_content = []
        # make tooltips
        for i in range(len(objects)):
            label = df.ix[[i], :].T
            label.columns = ['Object {0}'.format(i)]

            # .to_html() is unicode; so make leading 'u' go away with str()
            tooltip_content.append(str(label.to_html()))


        if setup.feature_data_visible == "Yes":
            # all feature data is available in tooltip
            tooltip = mpld3.plugins.PointHTMLTooltip(scatter, tooltip_content,
                                                     voffset=-300, hoffset=10)
        else:
            # only x and y features are available in tooltip
            minimal_labels = [
                [headers[feature_x_id] + ": " + str(i[0]) + ", " + headers[feature_y_id] + ": " + str(i[1])]
                for i in objects]

            if dataset_type == "HIPE":
                for i in range(len(timestamps)):
                    # append also ids in restricted tooltip for better acknowledgement
                    minimal_labels[i].append(" id: " + str(timestamps[i]))

            tooltip = mpld3.plugins.PointHTMLTooltip(points=scatter, labels=minimal_labels, hoffset=10)

            a = []
            # only send available subspaces to the information field
            if selected_obj != None:
                if dataset_type == "HIPE":
                    a.append(xy[selected_obj][0])  # id
                for feature in features:
                    a.append(xy[selected_obj][feature])
                xy = a

            b = []
            if dataset_type == "HIPE":
                b.append(headers[0])  # id
            for feature in features:
                b.append(headers[feature])
            headers = b

        mousepos = mpld3.plugins.MousePosition(fontsize=12, fmt='.3g')

        mpld3.plugins.connect(fig, tooltip, mousepos)

        if setup.feedback_mode != "system":
            mpld3.plugins.connect(fig, ClickInfo(scatter))

        figid = "graph_subspace_" + subspace_id + "_div"

        html_graph = mpld3.fig_to_html(fig, figid=figid, template_type="best")
        plt.close()

        return html_graph, xy, headers, figid, tooltip_content, subspace_id

    def get_raw_data_visualization(self, dataset, obj_id):
        if dataset.type == 'MNIST':
            raw_file = dataset.raw_file
            file_text = raw_file.read()
            dict_pixels = json.loads(file_text)
            fig_pixels = dict_pixels[obj_id]
            pixels = list()
            for pixel in fig_pixels:
                new_pixel = 255 * (1.0 - pixel)
                pixels.append(new_pixel)
            pixels = np.array(pixels)
            pixels.resize((28, 28))
            im = Image.fromarray(pixels.astype(np.uint8), mode='L')
            im = im.resize((140, 140))
            im = ImageOps.expand(im, border=50, fill='black')
            path = "media/mnist_" + str(dataset.id) + "_" + str(obj_id) + ".png"
            im.save(path)  # temp save
            return path

        elif dataset.type == 'HIPE':

            plt.close("all")

            with open(dataset.raw_file.path) as data_file:
                hipejson = json.load(data_file)

            hipedf = pd.DataFrame(hipejson)
            hipedf_t = hipedf.T
            hipedf_t.iloc[obj_id]['SensorDateTime'] = pd.to_datetime(hipedf_t.iloc[obj_id]['SensorDateTime'],
                                                                     errors='coerce')
            hipedf_t.iloc[obj_id]['SensorDateTime'] = hipedf_t.iloc[obj_id]['SensorDateTime'].to_pydatetime()

            for col in hipedf_t.columns:
                if col != 'SensorDateTime':
                    fig = pyplot.figure()
                    hipedf_t.iloc[obj_id][col] = pd.to_numeric(hipedf_t.iloc[obj_id][col])
                    pyplot.plot(hipedf_t.iloc[obj_id]['SensorDateTime'].tolist(), hipedf_t.iloc[obj_id][col].tolist(),
                                linewidth=0.5)
                    legend = []
                    legend.append(col)
                    pyplot.legend(legend, loc="best")
                    fig.autofmt_xdate()

            path = "media/hipe_" + str(dataset.id) + "_" + str(obj_id) + ".pdf"

            pdf = p.PdfPages(path)
            for f in xrange(1, pyplot.gcf().number + 1):
                pdf.savefig(f)
            pdf.close()

            return path