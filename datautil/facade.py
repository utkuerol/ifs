from datautil.jsonservices import DatasetAPIInfoJSONMaker, OcalAPIRequestJSONMaker, JSONExporter, SetupGridPointsMaker, \
    MinMax, OcalAPICommunicationService
from datautil.jsonservices import OcalApiService
from datautil.visualizationservices import Visualizer


class Facade:

    @staticmethod
    def validate_feature_data_format(feature_file, type):
        success = False
        if type == "HIPE":
            try:
                MinMax.normalize_hipe(feature_file)
                success = True
            except:
                success = False
        elif type == "MNIST":
            try:
                MinMax.normalize_mnist(feature_file)
                success = True
            except:
                success = False
        return success

    @staticmethod
    def validate_raw_data_format(raw_file, type):
        success = True
        # here to implement the validations required for the raw data files
        return success

    @staticmethod
    def prepare_dataset_data(dataset):
        dataset_api_info_json_maker = DatasetAPIInfoJSONMaker(dataset)
        return dataset_api_info_json_maker.prepare_data()

    @staticmethod
    def prepare_ocal_api_request(session):
        ocal_api_request_json_maker = OcalAPIRequestJSONMaker(session)
        return ocal_api_request_json_maker.make_json()  # collect all important data in one json file

    @staticmethod
    def prepare_setup_data(setup):
        setup_grid_points_maker = SetupGridPointsMaker(setup)
        return setup_grid_points_maker.prepare_setup_info()

    @staticmethod
    def export_session(session):
        session_exporter = JSONExporter()
        file = session_exporter.export(session)
        return file

    @staticmethod
    def export_all_sessions(sessions_list):
        session_exporter = JSONExporter()
        return session_exporter.export_all(sessions_list)

    @staticmethod
    def get_classifier_visualization(iteration, subspace, selected_obj, *args):
        classifier_visualizer = Visualizer()
        content = classifier_visualizer.get_classifer_visualization(iteration, subspace, selected_obj, args[0])
        return content

    @staticmethod
    def get_raw_data_visualization(dataset, object_id):
        raw_data_visualizer = Visualizer()
        return raw_data_visualizer.get_raw_data_visualization(dataset, object_id)

    @staticmethod
    def get_subspaces_rankings(last_iteration):
        rankings_dict = OcalApiService.get_subspaces_rankings(last_iteration)
        return rankings_dict

    @staticmethod
    def get_ocal_prediction(output, query_id):
        ocal_prediction = OcalApiService.get_ocal_prediction(output, query_id)
        return ocal_prediction

    @staticmethod
    def get_query_object_id(output, input):
        query_object_id = OcalApiService.get_query_object_id(output, input)
        return query_object_id

    @staticmethod
    def check_ocal_output(ocal_output):
        ocal_out_message = OcalApiService.check_ocal_output(ocal_output)
        return ocal_out_message

    @staticmethod
    def get_last_iteration_output(ocal_input):
        ocal_out_put = OcalAPICommunicationService.get_last_iteration_output(ocal_input)
        return ocal_out_put
