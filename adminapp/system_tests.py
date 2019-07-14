from unittest import mock

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from adminapp.models import Dataset, Setup, Session
from adminapp.services import DatasetService


class TestExperiment(TestCase):
    c = Client()

    def setUp(self):
        dataset = Dataset.objects.create(id=9, name='test', description='desc', type='HIPE',
                                         feature_file='WashingMachine_PhaseCount_3_geq_2017-10-23_lt_2017-10-30_agg_day.csv',
                                         raw_file='WashingMachine_PhaseCount_3_geq_2017-10-23_lt_2017-10-30.json')
        _dataset_service = DatasetService()
        _dataset_service.save_dataset_info(9)

        user = User.objects.create(username='admin', id=1, is_superuser=True)
        user.save()
        user2 = User.objects.create(username="user", id=2)
        user2.save()
        self.c.force_login(user, None)

    def tearDown(self):
        pass

    def test_create_setup_and_view(self):
        # create new setup
        response = self.c.post(reverse('new-setup'),
                               {'dataset_id': ['9'], 'name': ['test_setup'], 'description': ['test'],
                                'classifier': ['SVDDneg'], 'gamma': ['0.4'], 'cost_function': ['0.1'],
                                'query_strategy': ['RandomQs'], 'feedback_mode': ['system'],
                                'number_of_iterations': ['3'], 'unknown_allowed': ['Yes'],
                                'raw_data_visible': ['Yes'], 'feature_data_visible': ['Yes'],
                                'subspace_set-TOTAL_FORMS': ['2'], 'subspace_set-INITIAL_FORMS': ['0'],
                                'subspace_set-MIN_NUM_FORMS': ['0'], 'subspace_set-MAX_NUM_FORMS': ['1000'],
                                'subspace_set-0-feature_x_id': ['2'], 'subspace_set-0-feature_y_id': ['3'],
                                'subspace_set-0-gridpoints_x': ['30'], 'subspace_set-0-gridpoints_y': ['30'],
                                'subspace_set-1-feature_x_id': ['5'], 'subspace_set-1-feature_y_id': ['3'],
                                'subspace_set-1-gridpoints_x': ['30'],
                                'subspace_set-1-gridpoints_y': ['30']}, follow=True)

        self.assertEqual(Setup.objects.last().name, 'test_setup')

        # check if redirected after creation
        self.assertRedirects(response, '/adminapp/setups/1/', status_code=302, target_status_code=200)
        self.assertEqual(response.context['setup'].name, 'test_setup')

        # go to setups list page
        response = self.c.get(reverse('setup-list'))

        self.assertEqual(response.context['setups'][0].name, 'test_setup')

    def test_clone_setup(self):
        self.test_create_setup_and_view()

        # clone setup
        response = self.c.post('/adminapp/setups/1/', {'action': 'clone'}, follow=True)

        self.assertEqual(Setup.objects.last().name, 'test_setup (1)')

        # check if redirected after clone
        self.assertRedirects(response, '/adminapp/setups/2/', status_code=302, target_status_code=200)
        self.assertEqual(response.context['setup'].name, 'test_setup (1)')

    def mock_check_setup(setup):
        return "success"

    @mock.patch('adminapp.services.SetupService.check_setup', side_effect=mock_check_setup)
    def test_start_experiment(self, mock_check_setup):
        self.test_create_setup_and_view()
        # start experiment
        response = self.c.post('/adminapp/setups/1/', {'action': 'start_experiment'}, follow=True)

        self.assertEqual(Setup.objects.last().status, 'final')

    def test_invite_users(self):
        self.test_start_experiment()

        response = self.c.post(reverse('session-create'),
                               {'setup_id': ['1'], 'user_ids': ['1', '2']}, follow=True)

        self.assertIsNotNone(Session.objects.get(setup_id=1, user_id=1))
        self.assertIsNotNone(Session.objects.get(setup_id=1, user_id=2))
        self.assertRedirects(response, '/adminapp/experiments/', status_code=302, target_status_code=200)
