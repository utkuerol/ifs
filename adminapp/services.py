from datetime import datetime

from django.contrib.auth.models import User

from adminapp.models import Dataset, Setup, Session, Subspace
from datautil.facade import Facade


class DatasetService:
    """
    Provides business logic for datasets.
    """

    def save_dataset_info(self, dataset_id):
        self._save_api_feature_data(dataset_id)

    def _save_api_feature_data(self, dataset_id):
        """
        Gets dataset from database by dataset_id, sends its feature data file path to DataUtil and saves the returned normalized data in dataset.
        """
        dataset = Dataset.objects.get(id=dataset_id)
        json_data = Facade.prepare_dataset_data(dataset)  # normalize data and convert it to json
        dataset.normalized_feature_JSON = json_data
        dataset.save()  # save normalized data in models


class SetupService:
    """
        Provides business logic for Setup.
    """

    def clone_setup(self, setup_id):
        """
                Gets setup by setup_id and saves a new copy of this setup. The name of the setup is changed accordingly.
        """
        setup = Setup.objects.get(id=setup_id)
        setup.pk = None  # copy all fields except the primary key (id)
        setup.date = datetime.now()

        i = 1

        while len(Setup.objects.filter(name=setup.name + " (" + str(i) + ")")) != 0:
            i = i + 1

        setup.name += " (" + str(i) + ")"

        if setup.status == "final":
            setup.status = "draft"
        setup.save()

        new_subspaces = Subspace.objects.filter(setup_id=setup_id)

        for subspace in new_subspaces:
            subspace.setup_id = setup
            subspace.pk = None
            subspace.save()

        return Setup.objects.get(pk=setup.pk)

    def set_final(self, setup_id):
        """
                Sets the status of the given setup to "final".
        """
        setup = Setup.objects.get(id=setup_id)
        if setup.status == "draft":
            try:
                self.save_setup_info(setup)
            except:
                return "failed: failed building gridpoints. (Check your subspaces values)"
            success_msg = SetupService.check_setup(setup)
            if success_msg == "success":
                setup.status = 'final'
                setup.save()
            return success_msg

    @staticmethod
    def save_setup_info(setup):
        """
        save the gridpoints infor for a setup
        :param setup: setup object
        """
        grids = Facade.prepare_setup_data(setup)
        setup.subspaces_gridpoints_JSON = grids
        setup.save()

    def export_all(self, setup_id):
        """
        export all sessions of the selected setup
        :param setup_id: selected setup
        :return:
        """
        sessions = Session.objects.filter(setup_id_id=setup_id, status='accepted').order_by('id')
        json_string = Facade.export_all_sessions(sessions)
        return json_string

    @staticmethod
    def check_setup(setup):
        """
        check the correctness of the setup information by sending it to ocalapi and waiting for an answer.
        :param setup: setup to be checked
        :return: success if success and message error if something wrong occurs
        """
        user_created = False
        if User.objects.filter(username="test_user_" + str(setup.id)).count() == 0:
            user = User.objects.create_user("test_user_" + str(setup.id))
            user_created = True
        else:
            user = User.objects.get(username="test_user_" + str(setup.id))
        session = Session.objects.create(setup_id=setup, user_id=user, status="inactive")  # temp session to test setup
        session.save()
        ocal_input = Facade.prepare_ocal_api_request(session)
        session.delete()
        if user_created:
            user.delete()
        if ocal_input[:4] == "fail":
            return "Failed collecting input. Tag : (" + ocal_input[5:] + ")."
        ocal_output = Facade.get_last_iteration_output(ocal_input)
        ocal_output_message = Facade.check_ocal_output(ocal_output)
        if ocal_output_message != "success":
            return ocal_output_message
        else:
            return "success"


class SessionService:
    """
        Provides business logic for Session.
    """

    def create_inactive_session_from_invitation(self, setup_id, user_id):
        """
                Creates a inactive experiment session with setup information and places the participating user in it.
        """
        session = Session.objects.create(setup_id=Setup.objects.get(id=setup_id), user_id=User.objects.get(id=user_id),
                                         status="inactive")

    def get_finished_sessions_for_setup(self, setup_id):
        """
               Gets the list of sessions with status "finished" belonging to setup.
         """
        sessions = Session.objects.filter(setup_id=setup_id, status__in=['finished', 'accepted'])
        return sessions

    def set_accepted(self, session_id):
        """
                Sets the status of the given session to "accepted"
        """
        session = Session.objects.get(id=session_id)
        if session.status == "finished":
            session.status = "accepted"
        session.save()

    def export_session_results(self, session_id):
        """
                Gets the session by session_id, sends it to DataUtil.JSONExporter, returns the produced file.
        """
        session = Session.objects.get(id=session_id)
        file = Facade.export_session(session)
        return file

    @staticmethod
    def filter_sessions_by_status(user_id, status):
        """
        filters sessions by specific status for a user
        :return: session with this status for this user
        """
        return Session.objects.filter(user_id=user_id, status=status)
