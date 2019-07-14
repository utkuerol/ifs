from django.contrib.auth.models import User
from django.test import TestCase, Client

from adminapp.models import Dataset, Session, Setup
from adminapp.services import DatasetService


class TestUser(TestCase):
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
        self.c.force_login(user2, None)

        setup = Setup.objects.create(id=1, name='test_setup', status='final', dataset_id_id=9)
        setup.save()
        session1 = Session.objects.create(id=5, setup_id_id=1, user_id_id=2)
        session1.save()

    def tearDown(self):
        pass

    def test_ongoing_sessions(self):
        session = Session.objects.get(id=5)
        session.status = "ongoing"
        session.save()

        response = self.c.get('/userapp/2/ongoing_experiments', follow=True)

        self.assertIsNotNone(response.context['sessions'][0])
        self.assertEqual(response.context['sessions'][0].id, 5)
