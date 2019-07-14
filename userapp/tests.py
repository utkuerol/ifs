import datetime
from unittest import TestCase
from django.core.files import File
from django.contrib.auth.models import User
from adminapp.models import Setup, Session, Iteration, Subspace, Dataset, SubspaceUserInteractionStats
from userapp.services import UserStatsService, SessionService, IterationService

class TestSessionService(TestCase):

    def test_get_experiment_info(self):

        dataset = TestUserStatsService._create_dataset("testing_Dataset2")
        setup = TestUserStatsService._create_setup("testing_Setup2", dataset)
        user = TestUserStatsService._create_user("testing_User2")
        session = TestUserStatsService._create_session(setup, user)
        ocal_output_file = open("test_data/testResponse.json", "r")
        ocal_output = ocal_output_file.read()
        Iteration.objects.create(session_id_id=session.id, iteration_order=1,
                                             duration=10, ocal_prediction="inlier",
                                             user_feedback="outlier", ocal_output = ocal_output,
                                             ocal_query_id=1)
        Iteration.objects.create(session_id_id=session.id, iteration_order=2,
                                             duration=10, ocal_prediction="inlier",
                                             user_feedback="outlier", ocal_output=ocal_output,
                                             ocal_query_id=1)
        sessionService = SessionService()
        session_id = session.id
        ist_ExperimentInfo_dict = sessionService.get_experiment_info(session_id)
        must_ExperimentInfo_dict ={'session_id': session_id, 'iteration_order': 2,
                                   'remaining_iterations': 8, 'setup_name': 'testing_Setup2',
                                   'ocal_query_id': 1, 'ocal_prediction': 'inlier', 'subspaces_ordered': {}}

        self.assertTrue(ist_ExperimentInfo_dict == must_ExperimentInfo_dict)

    def test_set_session_status(self):
        dataset = TestUserStatsService._create_dataset("testing_Dataset5")
        setup = TestUserStatsService._create_setup("testing_Setup5", dataset)
        user = TestUserStatsService._create_user("testing_User5")
        session = TestUserStatsService._create_session(setup, user)
        sessionService = SessionService()
        sessionService.set_session_status(session, "finished")
        ist_status = session.status
        must_status = "finished"
        self.assertTrue(ist_status == must_status)

    def test_check_asked_object(self):
        dataset = TestUserStatsService._create_dataset("testing_Dataset7")
        setup = TestUserStatsService._create_setup("testing_Setup7", dataset)
        user = TestUserStatsService._create_user("testing_User7")
        session = TestUserStatsService._create_session(setup, user)
        sessionService = SessionService()
        Iteration.objects.create(session_id_id=session.id, iteration_order=1,
                                 duration=10, ocal_prediction="inlier",
                                 user_feedback="outlier",
                                 ocal_query_id=45)
        ist_true = sessionService.check_asked_object(session.id, 45)
        self.assertTrue(ist_true)

class TestUserStatsService(TestCase):


    def test_update_subspace_user_interaction_stats(self):
        dataset = TestUserStatsService._create_dataset("testing_Dataset3")
        setup = TestUserStatsService._create_setup("testing_Setup3", dataset)
        user = TestUserStatsService._create_user("testing_User3")
        session = TestUserStatsService._create_session(setup, user)
        iteration = TestUserStatsService._create_iteration(session)
        subspace = TestUserStatsService._create_subspace(setup, 0, 1)
        UserStatsService.update_subspace_user_interaction_stats(subspace.id, iteration.id, 7)
        subspace_user_interaction_stats = SubspaceUserInteractionStats.objects.get(subspace_id=subspace,
                                                                                   iteration_id=iteration)
        UserStatsService.update_subspace_user_interaction_stats(subspace.id, iteration.id, 7)
        subspace_user_interaction_stats = SubspaceUserInteractionStats.objects.get(
            id=subspace_user_interaction_stats.id)
        is_duration_value_true = subspace_user_interaction_stats.duration == 14
        self.assertTrue(is_duration_value_true)

    def test_update_iteration_duration(self):
        dataset = TestUserStatsService._create_dataset("testing_Dataset4")
        setup = TestUserStatsService._create_setup("testing_Setup4", dataset)
        user = TestUserStatsService._create_user("testing_User4")
        session = TestUserStatsService._create_session(setup, user)
        iteration = TestUserStatsService._create_iteration(session)
        UserStatsService.update_iteration_duration(5, iteration.id)
        iteration = Iteration.objects.get(id=iteration.id)
        self.assertTrue(iteration.duration == 15)



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
        setup = Setup.objects.create(name=name, number_of_iterations=10,
                                     dataset_id=dataset, raw_data_visible='false')
        return setup

    @staticmethod
    def _create_user(username):
        user = User.objects.create(username=username)
        return user

    @staticmethod
    def _create_session(setup, user):
        session = Session.objects.create(setup_id=setup, user_id=user)
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
