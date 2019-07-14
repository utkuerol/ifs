import os

from adminapp.models import Session, Iteration
from adminapp.models import Setup, Dataset, Subspace, SubspaceUserInteractionStats
from datautil.facade import Facade


class SessionService:
    """
    Provides the business logic regarding sessions.
    """

    @staticmethod
    def _get_subspaces_rankings(last_iteration):
        """
        Gets the subspaces of the last iteration ordered by their ocalapi rankings.
        :param last_iteration: to get the rankings for subspaces
        :return: ordered dict containing subspaces
        """
        subspaces_rankings_dict = Facade.get_subspaces_rankings(last_iteration)
        return subspaces_rankings_dict

    @staticmethod
    def start_session(session_id):
        """
        Starts the given session by setting its status to ongoing and creating the first iteration.
        :param session_id: session to start
        :return: success/error message
        """
        session = Session.objects.get(id=session_id)
        return_message = IterationService.create_next_iteration(session)
        if return_message == "success":
            SessionService.set_session_status(session, "ongoing")
            return "success"
        else:
            return return_message

    @staticmethod
    def get_experiment_info(session_id):
        """
        Gets the session from database using session_id, collects its
        experiment-relevant information (attributes of session, its last iteration and the raw data visualization
        file path from the regarding dataset object; if the session’s setup has raw_available set to true)
        :param session_id: to get the info about
        :return: dict containing experiment information
        """
        # get the last iteration for the current session
        last_iteration = Iteration.objects.filter(session_id=session_id).order_by('-iteration_order')[0]
        session = Session.objects.get(id=session_id)  # get the current session
        setup_id = session.setup_id.id
        setup = Setup.objects.get(pk=setup_id)
        iteration_order = last_iteration.iteration_order
        ocal_query_id = last_iteration.ocal_query_id
        ocal_prediction = last_iteration.ocal_prediction
        setup_name = setup.name
        number_of_iterations = setup.number_of_iterations
        remaining_iterations = number_of_iterations - iteration_order

        experiment_info = {'session_id': session_id, 'iteration_order': iteration_order,
                           'remaining_iterations': remaining_iterations,
                           'setup_name': setup_name, 'ocal_query_id': ocal_query_id,
                           'ocal_prediction': ocal_prediction}  # all important information in one dictionary
        subspaces_rankings_dict = SessionService._get_subspaces_rankings(last_iteration)
        experiment_info.update({'subspaces_ordered': subspaces_rankings_dict})
        if setup.raw_data_visible == 'true':
            dataset_id = setup.dataset_id
            dataset = Dataset.objects.get(pk=dataset_id)
            raw_data_visualization_path = dataset.raw_data_visualization.path
            # if the setup allows the visualization of the raw data,add the row data visualization file path to the dict
            experiment_info.update({'raw_data_visualization_path': raw_data_visualization_path})
            return experiment_info

        return experiment_info

    @staticmethod
    def set_session_status(session, status):
        """
        Sets the status of the session as "status".
        """
        session.status = status
        session.save()

    @staticmethod
    def filter_sessions_by_status(user_id, status):
        """
        Filters sessions of user by status
        :param user_id: owner of sessions
        :param status: to filter by
        :return: list of sessions
        """
        return Session.objects.filter(user_id=user_id, status=status)

    @staticmethod
    def get_raw_data_visualization(dataset, object_id):
        """
        Gets the raw data visualization image path
        :param dataset: to look for the object
        :param object_id: to visualize
        :return: image path
        """
        return Facade.get_raw_data_visualization(dataset, object_id)

    @staticmethod
    def check_asked_object(session_id, selected_obj):
        iterations = Iteration.objects.filter(session_id_id=session_id)
        last_iteration = Iteration.objects.filter(session_id=session_id).latest('iteration_order')
        for iteration in iterations:
            if iteration != last_iteration:
                if iteration.ocal_query_id == selected_obj:
                    return True
        return False


class UserStatsService:
    """
    Responsible for the updates on user statistics.
    """

    @staticmethod
    def update_subspace_user_interaction_stats(subspace_id, iteration_id, duration):
        """
        Gets the SubspaceUserInteractionStats updates its duration with the given duration.
        :param subspace_id:
        :param iteration_id:
        :param duration: recorded duration
        """
        # check if an object for these values exists
        try:
            subspace = Subspace.objects.get(id=subspace_id)
            iteration = Iteration.objects.get(id=iteration_id)

            subspace_user_interaction_stats = SubspaceUserInteractionStats.objects.get(subspace_id=subspace,
                                                                                       iteration_id=iteration)
        except SubspaceUserInteractionStats.DoesNotExist:
            subspace_user_interaction_stats = None

        # if the object doesnt exist then create one for given subspace and iteration
        if subspace_user_interaction_stats is None:
            SubspaceUserInteractionStats.objects.create(subspace_id=subspace, iteration_id=iteration,
                                                        duration=duration)
        else:
            subspace_user_interaction_stats.duration += duration  # if the object exists ,update the duration value
            subspace_user_interaction_stats.save()

    @staticmethod
    def update_iteration_duration(duration, iteration_id):
        """
        update the duration of the given iteration
        :param duration: recorded
        :param iteration_id: to update
        """
        iteration = Iteration.objects.get(pk=iteration_id)
        iteration.duration += duration
        iteration.save()


class IterationService:
    """
    Provides the business logic of an experiment.
    """

    @staticmethod
    def get_ocal_prediction_of_selected_obj(iteration_id, selected_obj_id):
        """
        gets the global ocal prediction of the given object.
        :param iteration_id:
        :param selected_obj_id:
        :return: ocal prediction as string
        """
        iteration = Iteration.objects.get(id=iteration_id)
        return Facade.get_ocal_prediction(iteration.ocal_output, selected_obj_id)

    @staticmethod
    def _get_iteration_input(session):
        """
        gets the input to be sent to ocalapi
        :param session:
        :return: ocal input
        """
        facade = Facade()
        ocal_input = facade.prepare_ocal_api_request(session)
        return ocal_input

    @staticmethod
    def submit_iteration(iteration_id, user_feedback, selected_obj_id):
        """
        Template method to wrap required operations to submit an iteration.
        :param iteration_id: to be submitted
        :param user_feedback: given feedback
        :param selected_obj_id: for which the feedback was given
        """
        iteration = Iteration.objects.get(id=iteration_id)
        session = Session.objects.get(id=iteration.session_id_id)
        IterationService._update_iteration(iteration_id, user_feedback, selected_obj_id)
        IterationService.delete_temp_image(session.setup_id.dataset_id, selected_obj_id)
        if iteration.iteration_order < session.setup_id.number_of_iterations:
            return IterationService.create_next_iteration(session)
        else:
            return "success"

    # update iteration object (model) with the given feedback
    @staticmethod
    def _update_iteration(iteration_id, user_feedback, selected_obj_id):

        iteration = Iteration.objects.get(id=iteration_id)

        iteration.user_feedback = user_feedback
        if iteration.ocal_query_id is not None and selected_obj_id != iteration.ocal_query_id:
            iteration.ocal_query_id = selected_obj_id
            ocal_prediction = Facade.get_ocal_prediction(iteration.ocal_output, selected_obj_id)
            iteration.ocal_prediction = ocal_prediction
        else:
            iteration.ocal_query_id = selected_obj_id
            ocal_prediction = Facade.get_ocal_prediction(iteration.ocal_output, selected_obj_id)
            iteration.ocal_prediction = ocal_prediction

        iteration.save()

    @staticmethod
    def create_next_iteration(session):
        """
        Creates the the next iteration with the iteration order being the successive integer of the last iterations
        iteration order.
        :param session: to create the iteration for
        :return: success/error message
        """
        ocal_input = IterationService._get_iteration_input(session)
        if ocal_input[:4] == "fail":
            return "Failed collecting input. Tag : (" + ocal_input[5:] + ")."
        ocal_output = Facade.get_last_iteration_output(ocal_input)
        ocal_output_message = Facade.check_ocal_output(ocal_output)
        if ocal_output_message != "success":
            return ocal_output_message
        number_of_iterations = Iteration.objects.filter(session_id=session).count()
        order = number_of_iterations + 1
        query_id = Facade.get_query_object_id(ocal_output, ocal_input)
        ocal_prediction = Facade.get_ocal_prediction(ocal_output, query_id)
        setup = session.setup_id
        if setup.feedback_mode != "user":
            iteration = Iteration.objects.create(session_id=session, iteration_order=order, ocal_query_id=query_id,
                                                 ocal_output=ocal_output, ocal_prediction=ocal_prediction)
        else:
            iteration = Iteration.objects.create(session_id=session, iteration_order=order,
                                                 ocal_output=ocal_output)
        iteration.save()
        return "success"

    @staticmethod
    def delete_iteration(iteration_id):
        """
        deletes the given iteration
        :param iteration_id: to delete
        """
        iteration = Iteration.objects.get(id=iteration_id)
        iteration.delete()

    @staticmethod
    def get_classifier_results_visualization(iteration_id, subspace_id, obj_id, *args):
        """
        Calls the _datautil_facade method get_classifier_visualization and returns the returned HTML- String.
        :param iteration_id: to visualize
        :param subspace_id: to visualize
        :param obj_id: selected object to mark on the visualization
        :return: visualization content including information about the feature values of the subspace objects
        """
        facade = Facade()
        content = facade.get_classifier_visualization(iteration_id, subspace_id, obj_id, args[0])
        return content

    @staticmethod
    def delete_temp_image(dataset, obj_id):
        """
        Deletes the temporary raw data visualization images from the system
        :param dataset:
        :param obj_id:
        """

        if not obj_id and str(obj_id) != "0":
            return
        type = dataset.type
        file_path = "media/" + str(type).lower() + "_" + str(dataset.id) + "_" + str(obj_id)
        if type == "HIPE":
            file_path += ".pdf"
        elif type == "MNIST":
            file_path += ".png"
        try:
            os.remove(file_path)
        except Exception as e:
            pass
