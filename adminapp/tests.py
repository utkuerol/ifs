from collections import OrderedDict
from datetime import datetime

from django.contrib.auth.models import User
from django.core.files import File
from unittest import TestCase

from adminapp.models import Dataset, Setup, Session

from adminapp.services import SetupService

from adminapp.services import SessionService

'''
     Test class Setupservices 
'''


class TestSetupServices(TestCase):
    """
        Test method clone_setup
    """

    def test_clone_setup(self):
        dataset = TestSetupServices.create_dataset("test_dataset3")
        setup = TestSetupServices.create_setup("test_setup3", dataset)
        setupservices = SetupService()
        cloned_setup = setupservices.clone_setup(setup.id)
        is_cloned_fields_identical = TestSetupServices._is_cloned_fields_identical(setup, cloned_setup)

        if cloned_setup.name == setup.name + " (" + str(1) + ")":
            is_name_ok = True
        else:
            is_name_ok = False

        if cloned_setup.status == "draft":
            is_status_ok = True
        else:
            is_status_ok = False

        if setup.id != cloned_setup.id:
            is_id_ok = True
        else:
            is_id_ok = False

        is_all_fields_ok = is_cloned_fields_identical and is_name_ok and is_status_ok and is_id_ok
        self.assertTrue(is_all_fields_ok)

    """
         Check if all fields except id, name, status are identical
    """

    @staticmethod
    def _is_cloned_fields_identical(setup, cloned_setup):
        if setup.dataset_id == cloned_setup.dataset_id \
                and setup.number_of_iterations == cloned_setup.number_of_iterations \
                and setup.raw_data_visible == cloned_setup.raw_data_visible \
                and setup.classifier == cloned_setup.classifier \
                and setup.cost_function == cloned_setup.cost_function \
                and setup.gamma == cloned_setup.gamma \
                and setup.query_strategy == cloned_setup.query_strategy \
                and setup.unknown_allowed == cloned_setup.unknown_allowed:
            return True
        else:
            return False

    """
         Method to create a new dataset
    """

    @staticmethod
    def create_dataset(name):
        feature_data_file = File(open('test_data/test_hipe.csv', 'r'))
        row_data_file = File(open('test_data/WashingMachine_PhaseCount_3_geq_2017-10-01_lt_2018-01-01.json',
                                  'r'))
        dataset = Dataset.objects.create(name=name, type="HIPE", feature_file=feature_data_file,
                                         raw_file=row_data_file)
        return dataset

    """
         Method to create a new setup
    """

    @staticmethod
    def create_setup(name, dataset):
        setup = Setup.objects.create(dataset_id=dataset, name=name, description="for testing",
                                     feedback_mode="User", status="draft")
        return setup


"""
            Test class SessionServices
"""


class TestSessionServices(TestCase):
    """
            Test method set_accepted
    """

    def test_set_accepted(self):

        dataset = TestSetupServices.create_dataset("test_dataset4")
        setup = TestSetupServices.create_setup("test_setup4", dataset)
        user = User.objects.create_user(username='Alaa',
                                        email='alaa.mousa@web.de',
                                        password='secret')
        session = Session.objects.create(setup_id=setup, user_id=user,
                                         status="finished")
        sessionservice = SessionService()
        sessionservice.set_accepted(session.id)
        session = Session.objects.get(id=session.id)
        self.assertTrue(session.status == "accepted")

    def test_get_finished_sessions_for_setup(self):
        dataset = TestSetupServices.create_dataset("test_dataset5")
        setup = TestSetupServices.create_setup("test_setup5", dataset)
        user_1 = User.objects.create_user(username='Alaa_m',
                                          email='alaa.mousa@web.de',
                                          password='secret')
        user_2 = User.objects.create_user(username='Utku',
                                          email='Utku.1@web.de',
                                          password='password')
        Session.objects.create(setup_id=setup, user_id=user_1,
                               status="inactive")
        Session.objects.create(setup_id=setup, user_id=user_2,
                               status="finished")
        Session.objects.create(setup_id=setup, user_id=user_1,
                               status="inactive")
        Session.objects.create(setup_id=setup, user_id=user_2,
                               status="finished")
        sessionservice = SessionService()
        sessions = sessionservice.get_finished_sessions_for_setup(setup.id)
        for session in sessions:
            if session.status != "finished":
                is_finished_session = False
            else:
                is_finished_session = True

        self.assertTrue(is_finished_session)

    def test_filter_sessions_by_status(self):
        dataset = TestSetupServices.create_dataset("test_dataset6")
        setup = TestSetupServices.create_setup("test_setup6", dataset)
        user_3 = User.objects.create_user(username='Alaa.m',
                                          email='alaa.mousa@web.de',
                                          password='secret')
        user_4 = User.objects.create_user(username='Utku.E',
                                          email='Utku.1@web.de',
                                          password='password')
        Session.objects.create(setup_id=setup, user_id=user_3,
                               status="finished")
        Session.objects.create(setup_id=setup, user_id=user_4,
                               status="finished")
        Session.objects.create(setup_id=setup, user_id=user_3,
                               status="inactive")
        Session.objects.create(setup_id=setup, user_id=user_4,
                               status="inactive")
        sessionservice = SessionService()
        is_sessions_for_user_3 = sessionservice.filter_sessions_by_status(user_3, "inactive")
        for session in is_sessions_for_user_3:
            if session.status != "inactive" or session.user_id != user_3:
                is_filtered_session_ok = False

            else:
                is_filtered_session_ok = True

            self.assertTrue(is_filtered_session_ok)


