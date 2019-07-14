import abc
import json
from builtins import list, range, staticmethod, Exception, dict
from collections import OrderedDict

import numpy as np
import pandas
import pandas as pd
import requests
from django.contrib.auth.models import User
from sklearn import preprocessing

from adminapp.models import Setup, Iteration, SubspaceUserInteractionStats, Subspace, Dataset, Session


class Normalizer(metaclass=abc.ABCMeta):
    """
    Abstract strategy class responsible for data
    normalization.
    """

    # return normalized data
    @staticmethod
    def normalize_hipe(self, data_file_path):
        pass

    @staticmethod
    def normalize_mnist(self, data_file_path):
        pass


class MinMax(Normalizer):
    """
    Concrete strategy class to perform a min-max normalization algorithm.
    """

    @staticmethod
    def normalize_mnist(data_file_path):
        """
        normalize feature data type mnist
        :param data_file_path:  path of mnist feature data file
        :return: normalized data frame
        """
        reader = pd.read_csv(data_file_path, header=0)
        df = pd.DataFrame(data=reader)
        column_names_to_normalize = [column for column in list(df)]
        column = df[column_names_to_normalize].values
        min_max_scaler = preprocessing.MinMaxScaler()
        columns_scaled = min_max_scaler.fit_transform(column)
        df_temp = pd.DataFrame(columns_scaled, columns=column_names_to_normalize, index=df.index)
        df[column_names_to_normalize] = df_temp
        return df

    @staticmethod
    def normalize_hipe(data_file_path):
        """
        normalize feature data type hipe
        :param data_file_path: path of hipe feature data file
        :return: normalized data frame
        """
        reader = pd.read_csv(data_file_path, header=0)
        df = pd.DataFrame(data=reader)
        # it is known that the hipe feature file must have an id column
        id_column_found = False
        for column in list(df):
            if column == "id":
                id_column_found = True
        if not id_column_found:
            raise Exception('Not in right format')
        column_names_to_normalize = [column for column in list(df) if column != "id"]
        column = df[column_names_to_normalize].values
        min_max_scaler = preprocessing.MinMaxScaler()
        columns_scaled = min_max_scaler.fit_transform(column)
        df_temp = pd.DataFrame(columns_scaled, columns=column_names_to_normalize, index=df.index)
        df[column_names_to_normalize] = df_temp
        return df


class DatasetAPIInfoJSONMaker:
    """
    Responsible for the preparation of the OcalAPI information of a dataset.
    """

    def __init__(self, dataset):
        self.dataset = dataset

    def prepare_data(self):
        """
        Normalizes data by calling the MinMax methods
        :return: normalized feature data as json.
        """
        data_file_path = self.dataset.feature_file.path
        dataset_type = self.dataset.type
        if dataset_type == "HIPE":
            norm_data = MinMax.normalize_hipe(data_file_path)

        elif dataset_type == "MNIST":
            norm_data = MinMax.normalize_mnist(data_file_path)

        df_transposed_list = norm_data.values.T.tolist()
        json_to_return = json.dumps(df_transposed_list)

        return json_to_return


class SetupGridPointsMaker:
    """
    Responsible for the preparation the Grid points for the setup
    """

    def __init__(self, setup):
        self.setup = setup

    def prepare_setup_info(self):
        """
        Template method to wrap required operations to prepare the JSON File
        containing setup informations for the API.
        :return: Dictionary contains the Grid points (normalized,not normalized,visualization)
        """
        subspace_gridpoints = dict()
        subspace_gridpoints['normalized'] = self._make_normalized_gridpoints()
        subspace_gridpoints['not-normalized'] = self._make_gridpoints()
        subspace_gridpoints['visualization'] = self._make_visualization_gridpoints()
        subspace_gridpoints_json = json.dumps(subspace_gridpoints)
        return subspace_gridpoints_json

    def _make_normalized_gridpoints(self):
        """
        normalize grid points and return them
        """
        subspaces = Subspace.objects.filter(setup_id=self.setup.id)
        grids = []

        for subspace in subspaces:
            dataset = Dataset.objects.get(id=self.setup.dataset_id_id)

            if dataset.type == 'HIPE':
                x_id = subspace.feature_x_id
                y_id = subspace.feature_y_id

            elif dataset.type == 'MNIST':
                x_id = subspace.feature_x_id - 1
                y_id = subspace.feature_y_id - 1

            num_grids_x = subspace.gridpoints_x
            num_grids_y = subspace.gridpoints_y

            normalized_json = dataset.normalized_feature_JSON
            data = pandas.read_json(normalized_json)
            xs = data.iloc[x_id, :]
            ys = data.iloc[y_id, :]

            try:
                x_min = min(xs)
                x_max = max(xs)
                y_min = min(ys)
                y_max = max(ys)
            except IndexError as ie:
                print(ie)
                break

            grid_x = np.linspace(x_min - abs((x_max - x_min) / 10), x_max + abs((x_max - x_min) / 10), num_grids_x)
            grid_y = np.linspace(y_min - abs((y_max - y_min) / 10), y_max + abs((y_max - y_min) / 10), num_grids_y)

            grid_xy = np.transpose([np.tile(grid_x, len(grid_y)), np.repeat(grid_y, len(grid_x))]).tolist()

            grids.append(grid_xy)

        return grids

    def _make_gridpoints(self):
        """
        generates
        the grid points based on the maximal and minimal values of the features
        according to the number of grid points
        :return: generated grid points
        """

        subspaces = Subspace.objects.filter(setup_id=self.setup.id)
        grids = []

        for subspace in subspaces:
            dataset = Dataset.objects.get(id=self.setup.dataset_id_id)

            if dataset.type == 'HIPE':
                x_id = subspace.feature_x_id
                y_id = subspace.feature_y_id

            elif dataset.type == 'MNIST':
                x_id = subspace.feature_x_id - 1
                y_id = subspace.feature_y_id - 1

            num_grids_x = subspace.gridpoints_x
            num_grids_y = subspace.gridpoints_y

            datafile_path = dataset.feature_file.path

            data = pandas.read_csv(datafile_path, usecols=[x_id, y_id])

            try:
                if x_id < y_id:

                    x_min = min(data.iloc[:, 0])
                    x_max = max(data.iloc[:, 0])
                    y_min = min(data.iloc[:, 1])
                    y_max = max(data.iloc[:, 1])
                else:
                    x_min = min(data.iloc[:, 1])
                    x_max = max(data.iloc[:, 1])
                    y_min = min(data.iloc[:, 0])
                    y_max = max(data.iloc[:, 0])
            except IndexError as ie:
                print(ie)
                break

            grid_x = np.linspace(x_min - abs((x_max - x_min) / 10), x_max + abs((x_max - x_min) / 10), num_grids_x)
            grid_y = np.linspace(y_min - abs((y_max - y_min) / 10), y_max + abs((y_max - y_min) / 10), num_grids_y)

            grid_xy = np.transpose([np.tile(grid_x, len(grid_y)), np.repeat(grid_y, len(grid_x))]).tolist()
            grids.append(grid_xy)
        return grids

    def _make_visualization_gridpoints(self):
        """
        generate grid points for visualization

        """
        subspaces = Subspace.objects.filter(setup_id=self.setup.id)
        grids = []

        for subspace in subspaces:
            dataset = Dataset.objects.get(id=self.setup.dataset_id_id)

            if dataset.type == 'HIPE':
                x_id = subspace.feature_x_id
                y_id = subspace.feature_y_id

            elif dataset.type == 'MNIST':
                x_id = subspace.feature_x_id - 1
                y_id = subspace.feature_y_id - 1

            num_grids_x = subspace.gridpoints_x
            num_grids_y = subspace.gridpoints_y

            datafile_path = dataset.feature_file.path

            data = pandas.read_csv(datafile_path, usecols=[x_id, y_id])

            try:
                if x_id < y_id:

                    x_min = min(data.iloc[:, 0])
                    x_max = max(data.iloc[:, 0])
                    y_min = min(data.iloc[:, 1])
                    y_max = max(data.iloc[:, 1])
                else:
                    x_min = min(data.iloc[:, 1])
                    x_max = max(data.iloc[:, 1])
                    y_min = min(data.iloc[:, 0])
                    y_max = max(data.iloc[:, 0])

            except IndexError as ie:
                print(ie)
                break
            grid_xy = []

            grid_x = np.linspace(x_min - abs((x_max - x_min) / 10), x_max + abs((x_max - x_min) / 10),
                                 num_grids_x).tolist()
            grid_y = np.linspace(y_min - abs((y_max - y_min) / 10), y_max + abs((y_max - y_min) / 10),
                                 num_grids_y).tolist()

            grid_xy.append(grid_x)
            grid_xy.append(grid_y)

            grids.append(grid_xy)

        return grids


class OcalAPIRequestJSONMaker:
    """
    Responsible for the preparation of the OCAL API input
    """

    def __init__(self, session):
        self.session = session
        self.setup = Setup.objects.get(id=session.setup_id_id)
        self.dataset = Dataset.objects.get(id=self.setup.dataset_id_id)

    def make_json(self):
        """
        build json for ocalApi input
        """
        input_dict = self._build_input()
        if isinstance(input_dict, str) and input_dict[:4] == "fail":
            return input_dict
        json_input = json.dumps(input_dict, ensure_ascii=False, indent=2)
        return json_input

    def _build_input(self):
        """
        buils OCAL API input
        """
        input_dict = dict()
        # build data
        try:
            input_dict['data'] = self._get_data()
        except:
            return "fail_data"
        # build labels
        try:
            input_dict['labels'] = self._get_labels()
        except:
            return "fail_labels"
        # build params
        try:
            input_dict['params'] = self._get_params()
        except:
            return "fail_params"
        # build query_history
        try:
            input_dict['query_history'] = self._get_query_history()
        except:
            return "fail_query_history"
        # build subspaces
        try:
            input_dict['subspaces'] = self.get_subspaces()
        except:
            return "fail_subspaces"
        # build subspace_gridpoints
        try:
            input_dict['subspace_grids'] = self.get_subspace_grids()
        except:
            return "fail_subspace_grids"
        return input_dict

    def _get_data(self):
        """
        get the normalized data for the input
        """
        normalised_feature = self.dataset.normalized_feature_JSON
        normalised_list = json.loads(normalised_feature)
        if self.dataset.type == "HIPE":
            del normalised_list[0]
        transposed_list = np.array(normalised_list).T.tolist()
        return transposed_list

    def _get_labels(self):
        """
        get the current labels for this session
        """
        u_labels = self._generate_u_list()
        iterations = Iteration.objects.filter(session_id=self.session)
        for iteration in iterations:
            object_id = iteration.ocal_query_id
            new_label = ''
            if iteration.user_feedback == "inlier":
                new_label = 'Lin'
            elif iteration.user_feedback == "outlier":
                new_label = 'Lout'
            if new_label != '':
                u_labels[object_id] = new_label

        return u_labels

    def _generate_u_list(self):
        """
        generate a list with n Us, where n is the number of elements for this dataset
        """
        u_labels = list()
        number_of_elements = self._get_number_of_elements()
        for i in range(number_of_elements):
            u_labels.append("U")
        return u_labels

    def _get_number_of_elements(self):
        """
        return the numbers of the objects
        """
        normalised_feature = self.dataset.normalized_feature_JSON
        normalised_list = json.loads(normalised_feature)
        number_of_elements = len(normalised_list[0])
        return number_of_elements

    def _get_params(self):
        """
        return the setup parameters as dictionary
        """
        parameters_dict = dict()
        gamma = self.setup.gamma
        cost = self.setup.cost_function
        classifier = self.setup.classifier
        query_strategy = self.setup.query_strategy
        parameters_dict["gamma"] = gamma
        parameters_dict["C"] = cost
        parameters_dict["classifier"] = classifier
        parameters_dict["query_strategy"] = query_strategy
        return parameters_dict

    def _get_query_history(self):
        """
        return the query history as a list
        """
        iterations = Iteration.objects.filter(session_id=self.session).order_by('id')
        query_history = list()
        for iteration in iterations:
            iteration_history = list()
            object_id = iteration.ocal_query_id + 1
            iteration_history.append(object_id)
            query_history.append(iteration_history)
        return query_history

    def get_subspaces(self):
        """
        return a list of subspaces for this setup
        """
        subspaces_list = list()
        subspaces = Subspace.objects.filter(setup_id=self.setup).order_by('id')
        for subspace in subspaces:
            subspace_features = list()
            subspace_features.append(subspace.feature_x_id)
            subspace_features.append(subspace.feature_y_id)
            subspaces_list.append(subspace_features)
        return subspaces_list

    def get_subspace_grids(self):
        """
        return the normalized grid points for this subspace
        """
        gridpoints = json.loads(self.setup.subspaces_gridpoints_JSON)
        subspace_grids = gridpoints["normalized"]
        return subspace_grids


class Concluder(metaclass=abc.ABCMeta):
    """
    Abstract strategy class to conclude an experiment.
    """

    @staticmethod
    def conclude(sessions):
        pass


class MajorityConcluder(Concluder):
    """
    Concrete strategy class for the abstract
    strategy Concluder.
    """

    @staticmethod
    def conclude(sessions):
        """
        Uses a simple algorithm to define a single labeling array (potential
        groundtruth) by always deciding according to the majority. Looks up
        each iteration of all given sessions and counts for each iteration
        different labelings, takes the one with the majority and puts the
        labeling in a new array. In the end it returns this new labeling array
        in JSON format.
        :param sessions: list of sessions to conclude from
        """
        labeled_objects = dict()
        for session in sessions:
            for iteration in Iteration.objects.filter(session_id=session.id):
                object = iteration.ocal_query_id
                label = iteration.user_feedback
                if object in labeled_objects:
                    labels = labeled_objects[object]
                    labels.append(label)
                    labeled_objects[object] = labels
                else:
                    labels = list()
                    labels.append(label)
                    labeled_objects[object] = labels
        return_dict = dict()
        for object in labeled_objects:
            inlier = 0
            outlier = 0
            result = "neutral"
            for label in labeled_objects[object]:
                if label == "inlier":
                    inlier += 1
                elif label == "outlier":
                    outlier += 1
            if inlier > outlier:
                result = "inlier"
            elif inlier < outlier:
                result = "outlier"
            return_dict[object] = result
        return return_dict


class SessionExporter(metaclass=abc.ABCMeta):
    """
    Abstract strategy class responsible for exporting session results.
    """

    @staticmethod
    def export(session):
        """
        Exports the result of a session.
        :param session: session to export
        :return: results as json
        """
        pass

    @staticmethod
    def export_all(sessions):
        """
        Exports results of multiple sessions. This also includes a section
        providing information on a potential Ground Truth which is received
        by calling the Concluder method conclude.
        :param sessions: list of sessions to export
        """
        pass


class JSONExporter(SessionExporter):
    """
    Concrete strategy class for the abstract strategy SessionExporter, having
    the output format JSON.
    """

    @staticmethod
    def export(session):
        """
        Implements the method in SessionExporter
        to export the session information
        with the output format JSON.
        :param session: session to export
        """
        session_dict = JSONExporter._get_json_dict(session)
        json_string = json.dumps(session_dict, ensure_ascii=False, indent=2)
        return json_string

    @staticmethod
    def export_all(sessions):
        """
        Implements the method in SessionExporter to export the session information
        with the output format JSON.
        :param sessions: list of sessions to export
        """
        output_dict = dict()
        counter = 1
        for session in sessions:
            json_string = JSONExporter.export(session)
            session_dict = json.loads(json_string)
            output_dict["session_" + str(counter)] = session_dict
            counter += 1
        output_dict["concluder"] = MajorityConcluder.conclude(sessions)
        json_string = json.dumps(output_dict, ensure_ascii=False, indent=2)
        return json_string

    @staticmethod
    def _get_json_dict(session):
        """
        return a dictionary contains some session's information
        :param session: session
        """
        session_dict = dict()
        information = JSONExporter._get_information(session)
        session_dict["Details"] = information
        iterations = JSONExporter._get_iterations(session)
        session_dict["Iterations"] = iterations
        classifier = JSONExporter._get_classifier(session)
        session_dict["Classifier labeling(by the last iteration)"] = classifier
        return session_dict

    @staticmethod
    def _get_information(session):
        """
        return a dictionary contains some session's information
        :param session: session
        """
        information = dict()
        information["session_id"] = session.id
        setup = Setup.objects.get(id=session.setup_id_id)
        information["dataset_name"] = setup.dataset_id.name
        information["setup_name"] = setup.name
        user = User.objects.get(id=session.user_id_id)
        information["user_name"] = user.username
        information["number_of_iterations"] = setup.number_of_iterations
        information["duration"] = JSONExporter._get_duration(session)
        return information

    @staticmethod
    def _get_duration(session):
        """
        return the duration of a session
        :param session: the session
        """
        iterations = Iteration.objects.filter(session_id=session.id)
        duration = 0
        time_calculated = False
        for iteration in iterations:
            if iteration.duration != 0:
                time_calculated = True
                duration += iteration.duration
        seconds = duration
        minutes = seconds // 60
        seconds = seconds % 60
        hours = minutes // 60
        minutes = minutes % 60
        if time_calculated:
            duration = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
        else:
            duration = 'not-available'
        return duration

    @staticmethod
    def _get_iterations(session):
        """
        return the list of informations for the iterations for this session
        """
        iterations = list()
        setup = session.setup_id
        number_of_iterations = setup.number_of_iterations
        for i in range(1, number_of_iterations + 1):
            iteration = JSONExporter._get_iteration(session, i)
            iterations.append(iteration)
        return iterations

    @staticmethod
    def _get_iteration(session, iteration):
        """
        return the information of the iteration
        """
        iteration_info = dict()
        iteration_info["order"] = iteration
        iteration = Iteration.objects.get(session_id=session.id, iteration_order=iteration)
        iteration_info["object_id"] = iteration.ocal_query_id
        iteration_info["ocal_prediction"] = iteration.ocal_prediction
        iteration_info["feedback"] = iteration.user_feedback
        duration = 'not-available'
        if iteration.duration != 0:
            duration = iteration.duration
            seconds = duration
            minutes = seconds // 60
            seconds = seconds % 60
            minutes = minutes % 60
            iteration_info["duration"] = '{:02d}:{:02d}'.format(minutes, seconds)
        else:
            iteration_info["duration"] = duration
        iteration_info["subspace(s)_used : duration"] = JSONExporter._get_subspaces(iteration.id)
        return iteration_info

    @staticmethod
    def _get_subspaces(iteration_id):
        """
        return information for the used subspace
        """
        subspaces_json = dict()
        used_subspaces = SubspaceUserInteractionStats.objects.filter(iteration_id=iteration_id)
        for subspace in used_subspaces:
            duration = 'not-used'
            if subspace.duration != 0:
                duration = subspace.duration
                seconds = duration
                minutes = seconds // 60
                seconds = seconds % 60
                hours = minutes // 60
                minutes = minutes % 60
                duration = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
            subspaces_json["(" + str(subspace.subspace_id.feature_x_id) + "," + str(subspace.subspace_id.feature_y_id)
                           + ")"] = duration
        return subspaces_json

    @staticmethod
    def _get_classifier(session):
        """
        return a list of global prediction for the last iteration
        """
        setup = Setup.objects.get(id=session.setup_id_id)
        number_of_iterations = setup.number_of_iterations
        iteration = Iteration.objects.get(session_id=session.id, iteration_order=number_of_iterations)
        if iteration.ocal_output:
            ocal_output = iteration.ocal_output
            dict = json.loads(ocal_output)
            try:
                labels = dict["prediction_global"]
                return labels
            except:
                return ""
        else:
            return ""


class OcalApiService:
    """
    class responsible for becoming some organized information from ocal output
    """

    @staticmethod
    def get_subspaces_rankings(last_iteration):
        """
        sort subspaces by there rankings and return them as dictionary
        :param last_iteration: the last iteration as object
        :return: dictionary of ordered subspaces with there rankings
        """
        session_id = last_iteration.session_id.id
        session = Session.objects.get(id=session_id)
        setup_id = session.setup_id
        setup_subspaces = Subspace.objects.filter(setup_id=setup_id).order_by('id')
        ocal_output = last_iteration.ocal_output
        ocal_output_dict = json.loads(ocal_output)
        subspaces_rankings = ocal_output_dict["ranking_subspaces"]
        subspaces_ids = [subspace.id for subspace in setup_subspaces]
        subspaces_ranking_dict = dict(zip(subspaces_ids, subspaces_rankings))
        sort_subspaces_ranking_dict = OrderedDict(sorted(subspaces_ranking_dict.items()
                                                         , key=lambda x: x[1]))
        to_return_sort_subspaces_ranking_dict = json.loads(json.dumps(sort_subspaces_ranking_dict))

        return to_return_sort_subspaces_ranking_dict

    @staticmethod
    def get_ocal_prediction(output, query_id):
        """
        return the ocal api prediction
        """
        output_dict = json.loads(output)
        prediction_global = output_dict["prediction_global"]
        ocal_prediction = prediction_global[query_id]
        return ocal_prediction

    @staticmethod
    def get_query_object_id(output, input):
        """
        calculate and return the id of the query object
        """
        output_dict = json.loads(output)
        query_ids = output_dict["query_ids"]
        query_id = query_ids[0]
        input_dict = json.loads(input)
        labels = input_dict["labels"]
        query_history = input_dict["query_history"]
        elements_counted = 0
        elements_not_counted = 0
        counter = 1
        for label in labels:
            is_in_history = False
            for history in query_history:
                if counter in history:
                    is_in_history = True
                    elements_not_counted += 1
            if not is_in_history:
                if label != "U":
                    elements_not_counted += 1
                else:
                    elements_counted += 1
            counter += 1
            if elements_counted == query_id:
                break
        element_to_be_asked = query_id + elements_not_counted
        return element_to_be_asked - 1

    @staticmethod
    def check_ocal_output(ocal_output):
        """
        handle the error messages of the OCAL API

        """

        if isinstance(ocal_output, str):
            if ocal_output == "Failed connecting to OcalApi":
                return ocal_output
        output_dict = json.loads(ocal_output)
        status = output_dict["status"]
        if status == 500:
            return "Failed reading input: " + output_dict["error"]
        elif status != 200:
            return "Failed :" + output_dict["error"]
        else:
            return "success"


class OcalAPICommunicationService:
    """
    calss responsible for the communication with OCALAPI
    """

    @staticmethod
    def get_last_iteration_output(ocal_input):
        import traceback
        """
        communicate with OCALAPI
        :param ocal_input: OCALAPI input
        """
        try:
            endpoint_file = open("ocalApi endpoint.json", "r")
            endpoint_data = endpoint_file.read()
            endpoint_config = json.loads(endpoint_data)

            url = endpoint_config["url"]
            headers = endpoint_config["headers"]
            request = requests.request("POST", url, data=ocal_input, headers=headers)
            output = request.text
            return output
        except Exception:
            traceback.print_exc()
            return "Failed connecting to OcalApi"


