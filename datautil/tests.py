import json
import os
from unittest import TestCase

import pandas as pd
from django.contrib.auth.models import User
from django.core.files import File

from adminapp.models import Session, Dataset, Setup, Iteration, Subspace, SubspaceUserInteractionStats
from datautil.jsonservices import DatasetAPIInfoJSONMaker, OcalAPICommunicationService, OcalApiService
from datautil.jsonservices import JSONExporter, SetupGridPointsMaker
from datautil.visualizationservices import Visualizer


class TestOcalApiService(TestCase):

    def test_get_subspaces_rankings(self):
        dataset = TestOcalApiService._create_dataset("testing_Dataset1")
        setup = TestOcalApiService._create_setup("testing_Setup1", dataset)
        user = TestOcalApiService._create_user("testing_User1")
        session = TestOcalApiService._create_session(setup, user)
        subspace_1 = TestOcalApiService._create_subspace(setup, 1, 2)
        subspace_2 = TestOcalApiService._create_subspace(setup, 2, 3)
        subspace_3 = TestOcalApiService._create_subspace(setup, 1, 3)
        ocal_output_file = open("test_data/testResponse.json", "r")
        ocal_output = ocal_output_file.read()
        iteration = Iteration.objects.create(session_id=session, iteration_order=1,
                                             duration=10, ocal_output=ocal_output)

        ocalApiService = OcalApiService()
        ist_dict = ocalApiService.get_subspaces_rankings(iteration)
        ist_dict_json = json.dumps(ist_dict)
        subspace_id = subspace_1.id
        must_dict = {subspace_id: 1}
        must_dict_json = json.dumps(must_dict)
        self.assertTrue(ist_dict_json == must_dict_json)

    @staticmethod
    def _create_dataset(name):
        feature_data_file = File(open('test_data/test_hipe.csv', 'r'))
        row_data_file = File(open('test_data/WashingMachine_PhaseCount_3_geq_2017-10-01_lt_2018-01-01.json',
                                  'r'))
        dataset = Dataset.objects.create(name=name, type="HIPE", feature_file=feature_data_file,
                                         raw_file=row_data_file)
        return dataset

    @staticmethod
    def _create_setup(name, dataset):
        setup = Setup.objects.create(name=name, number_of_iterations=10, dataset_id=dataset)
        return setup

    @staticmethod
    def _create_user(username):
        user = User.objects.create(username=username)
        return user

    @staticmethod
    def _create_session(setup, user):
        session = Session.objects.create(setup_id=setup, user_id_id=user.id)
        return session

    @staticmethod
    def _create_iteration(session):
        iteration = Iteration.objects.create(session_id_id=session.id, iteration_order=1,
                                             duration=10, ocal_prediction="inlier",
                                             user_feedback="outlier")
        return iteration

    @staticmethod
    def _create_subspace(setup, x, y):
        subspace = Subspace.objects.create(setup_id=setup, feature_x_id=x, feature_y_id=y)
        return subspace

    def test_get_ocal_prediction(self):
        ocal_output_file = open("test_data/testResponse.json", "r")
        ocal_output = ocal_output_file.read()
        ocalApiService = OcalApiService()
        ist_ocal_prediction = ocalApiService.get_ocal_prediction(ocal_output, 0)
        must_ocal_prediction = "outlier"
        self.assertTrue(ist_ocal_prediction == must_ocal_prediction)

    def test_check_ocal_output(self):
        ocal_output_file = open("test_data/testResponse.json", "r")
        ocal_output = ocal_output_file.read()
        ocalApiService = OcalApiService()
        ist_return = ocalApiService.check_ocal_output(ocal_output)
        must_return = "success"
        self.assertTrue(ist_return == must_return)


class TestExport(TestCase):

    def test_export_session(self):
        dataset = TestExport.create_dataset("testDataset")
        setup = TestExport.create_setup("testSetup", dataset)
        user = TestExport.create_user("testUser")
        session = TestExport.create_session(setup, user)
        for i in range(1, session.setup_id.number_of_iterations + 1):
            TestExport.create_iteration(session)
        for i in range(1, 6):
            subspace = TestExport.create_subspace(setup, 1, i)
            for iteration in Iteration.objects.all():
                TestExport.create_subspace_userinteraction(subspace, iteration)
        is_json = JSONExporter.export(session)
        is_dict = json.loads(is_json)
        must_file = open("test_data/data.json", "r")
        must_json = must_file.read()
        must_dict = json.loads(must_json)
        assert is_dict == must_dict

    @staticmethod
    def create_dataset(name):
        script_dir = os.path.dirname(__file__)
        feature_file_name = "resources/test/ChipPress_PhaseCount_3_geq_2017-10-01_lt_2018-01-01_agg_day.csv"
        raw_file_name = "resources/test/ChipPress_PhaseCount_3_geq_2017-10-01_lt_2018-01-01_agg_day.csv"
        feature_file_path = os.path.join(script_dir, feature_file_name)
        raw_file_path = os.path.join(script_dir, raw_file_name)
        dataset = Dataset.objects.create(name=name, type="MNIST", feature_file=feature_file_path,
                                         raw_file=raw_file_path)
        return dataset

    @staticmethod
    def create_setup(name, dataset):
        setup = Setup.objects.create(name=name, number_of_iterations=10, dataset_id_id=dataset.id)
        return setup

    @staticmethod
    def create_user(username):
        user = User.objects.create(username=username)
        return user

    @staticmethod
    def create_session(setup, user):
        session = Session.objects.create(id=100, setup_id_id=setup.id, user_id_id=user.id)
        return session

    @staticmethod
    def create_iteration(session):
        order = Iteration.objects.filter(session_id=session.id).count() + 1
        iteration = Iteration.objects.create(session_id_id=session.id, iteration_order=order,
                                             duration=10, ocal_prediction="inlier",
                                             user_feedback="outlier")
        return iteration

    @staticmethod
    def create_subspace(setup, x, y):
        subspace = Subspace.objects.create(setup_id_id=setup.id, feature_x_id=x, feature_y_id=y)
        return subspace

    @staticmethod
    def create_subspace_userinteraction(subspace, iteration):
        subspace_userinteraction = SubspaceUserInteractionStats.objects.create(subspace_id_id=subspace.id,
                                                                               iteration_id_id=iteration.id,
                                                                               duration=1)
        return subspace_userinteraction


class TestDatasetMaker(TestCase):

    def test_normalize_data_hipe(self):
        dataset = TestDatasetMaker.create_hipe_dataset("testHipeDataset")
        dataset_api_info_json_maker = DatasetAPIInfoJSONMaker(dataset)
        is_normalized_data_json = dataset_api_info_json_maker.prepare_data()
        must_norm_data_data_frame = pd.DataFrame({'id': ['01.10.2017', '2017-10-02', '03.10.2017'],
                                                  'IAVR_A__maximum': [0.25, 0.00, 1.00],
                                                  'IAVR_A__mean': [0.8, 0.0, 1.0],
                                                  'IAVR_A__mean_abs_change': [1.00, 0.75, 0.00], })
        df_transposed_list = must_norm_data_data_frame.values.T.tolist()
        must_norm_data_json = json.dumps(df_transposed_list)

        assert is_normalized_data_json == must_norm_data_json

    def test_normalize_data_mnist(self):
        dataset = TestDatasetMaker.create_mnist_dataset("testMnistDataset")
        dataset_api_info_json_maker = DatasetAPIInfoJSONMaker(dataset)
        is_normalized_data_json = dataset_api_info_json_maker.prepare_data()
        must_norm_data_data_frame = pd.DataFrame({'pca_1': [0.25, 0.00, 1.00],
                                                  'pca_2': [0.8, 0.0, 1.0],
                                                  'pca_3': [1.00, 0.75, 0.00]})
        df_transposed_list = must_norm_data_data_frame.values.T.tolist()
        must_norm_data_json = json.dumps(df_transposed_list)

        assert is_normalized_data_json == must_norm_data_json

    @staticmethod
    def create_hipe_dataset(name):
        feature_data_file = File(open('test_data/test_hipe.csv', 'r'))
        row_data_file = File(open('test_data/WashingMachine_PhaseCount_3_geq_2017-10-01_lt_2018-01-01.json',
                                  'r'))
        dataset = Dataset.objects.create(name=name, type="HIPE", feature_file=feature_data_file, raw_file=row_data_file)
        return dataset

    @staticmethod
    def create_mnist_dataset(name):
        feature_data_file = File(open('test_data/test_mnist.csv', 'r'))
        row_data_file = File(open('test_data/WashingMachine_PhaseCount_3_geq_2017-10-01_lt_2018-01-01.json',
                                  'r'))
        dataset = Dataset.objects.create(name=name, type="MNIST", feature_file=feature_data_file,
                                         raw_file=row_data_file)
        return dataset


class SetupGridpointsMaker(TestCase):

    def setUp(self):
        self.dataset = Dataset.objects.create(type="HIPE")
        self.setup = Setup.objects.create(dataset_id_id=self.dataset.id)
        self.subspace1 = Subspace.objects.create(setup_id_id=self.setup.id, feature_x_id=1, feature_y_id=2,
                                                 gridpoints_x=3, gridpoints_y=3)
        self.gridsmaker = SetupGridPointsMaker(self.setup)

    def tearDown(self):
        self.dataset.delete()
        self.setup.delete()
        self.subspace1.delete()

    def test_normalized_grids_on_valid_features(self):
        features = [["2017-10-01", "2017-10-02", "2017-10-03", "2017-10-04", "2017-10-05"], [0.2, 0.3, 0.205, 0.5, 0.8],
                    [0, 0.3, 0.205, 0.5, 0.9]]
        f_json = json.dumps(features)
        self.dataset.normalized_feature_JSON = f_json
        self.dataset.save()

        grids = [[[0.14, -0.09], [0.5, -0.09], [0.8600000000000001, -0.09], [0.14, 0.45000000000000007],
                  [0.5, 0.45000000000000007], [0.8600000000000001, 0.45000000000000007],
                  [0.14, 0.99], [0.5, 0.99], [0.8600000000000001, 0.99]]]
        self.assertCountEqual(self.gridsmaker._make_normalized_gridpoints(), grids)


class TestOcalAPICommunicationService(TestCase):
    import json

    input_file = open("test_data/testRequest.json", "r")
    input_json = input_file.read()
    output = OcalAPICommunicationService.get_last_iteration_output(input_json)
    output_dict = json.loads(output)

    must_file = open("test_data/testResponse.json", "r")
    must_json = must_file.read()
    must_dict = json.loads(must_json)

    # removing query_id
    output_dict['query_ids'] = 0
    must_dict['query_ids'] = 0


    assert must_dict["prediction_global"] == output_dict["prediction_global"]
    assert must_dict["prediction_subspaces"] == output_dict["prediction_subspaces"]

    for i in range(len(must_dict["score_subspace_grids"])):
        score_in_must = float(must_dict["score_subspace_grids"][0][i])
        score_in_output = float(output_dict["score_subspace_grids"][0][i])

        assert abs(score_in_must - score_in_output) < 0.000000001


class TestRawDataVisualization(TestCase):

    def setUp(self):
        self.hipedataset = Dataset.objects.create(name="raw_data_test", type="HIPE",
                                                  raw_file=File(open(
                                                      "test_data/WashingMachine_PhaseCount_3_geq_2017-10-23_lt_2017-10-30.json",
                                                      'r')))
        self.visualizer = Visualizer()

    def tearDown(self):
        self.hipedataset.delete()

    def test_output_filename_hipe(self):
        self.assertEqual(
            self.visualizer.get_raw_data_visualization(self.hipedataset, 0),
            "media/hipe_" + str(self.hipedataset.id) + "_" + str(0) + ".pdf")
