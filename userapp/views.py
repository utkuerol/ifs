# Create your views here.

import json
from itertools import chain

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DeleteView, DetailView

from userapp.services import *


class UserInvitationsListView(ListView):
    """
        View for the user experiment invitations page.

    """
    model = Session
    template_name = "user_invitations_list.html"
    context_object_name = 'sessions'
    paginate_by = 20

    def get_queryset(self):
        """
            Overrides the method to filter the list by status of sessions which have the status inactive
            :return: list invitations
        """
        session_service = SessionService()
        return session_service.filter_sessions_by_status(self.kwargs['pk'], "inactive")

    def post(self, request, *args, **kwargs):
        """
            Handles the buttons of the view that produce a POST request:
                    - Start Experiment: Calls the _session_service method start_session.
        """
        session_id = request.POST.get("sessionpk")
        pk = request.POST.get("pk")
        session_service = SessionService()
        result = session_service.start_session(session_id)
        if result == "success":
            return redirect("/userapp/" + pk + "/experiment/session=" + session_id)
        else:
            message = "Session " + str(session_id) + ": "
            message += result + " \n Please report this to the administrator"
            messages.warning(request, message)
            return redirect("/userapp/" + pk + "/invitations")


class UserOngoingSessionsListView(ListView):
    """
        View for the user ongoing experiments page
    """
    model = Session
    template_name = "user_ongoing_sessions_list.html"
    context_object_name = 'sessions'
    paginate_by = 20

    def get_queryset(self):
        """
            Overrides the method to filter the list by status of sessions which have the status ongoing
            :return: list invitations
        """
        session_service = SessionService()
        return session_service.filter_sessions_by_status(self.kwargs['pk'], "ongoing")

    def post(self, request, *args, **kwargs):
        """
            Handles "continue" button by redirecting to the experiment page.
        """
        session_id = request.POST.get("sessionpk")
        pk = request.POST.get("pk")
        return redirect("/userapp/" + pk + "/experiment/session=" + session_id)


class ExperimentView(View):
    """
    View for the experiment page.
    """
    _session_service = SessionService()
    _iteration_service = IterationService()

    def get(self, request, *args, **kwargs):
        """
        Prepares the content of the experiment page, which includes all the needed
        information about the current iteration. Handles also object and subspace selections if available.
        """

        session_id = kwargs["sessionpk"]
        session = Session.objects.get(id=session_id)

        # check illegal access via url to a non ongoing session
        if session.status != "ongoing":
            messages.warning(request,
                             "The session you tried to access is not an ongoing session. You are redirected to home page")
            return redirect(reverse_lazy('home'))

        # check illegal access via url to a session which doesnt belong to the current user
        if session.user_id != request.user:
            messages.warning(request, "Permission denied")
            return redirect(reverse_lazy('home'))

        setup = session.setup_id

        # info messages about feedback mode for the user
        if setup.feedback_mode == "system":
            messages.info(request,
                          "Feedback mode for your experiment is 'system'. This means you will receive the objects to evaluate directly from OcalApi and you can  give feedback only for this object.")

        elif setup.feedback_mode == "user":
            messages.info(request,
                          "Feedback mode for your experiment is 'user'. This means you won't receive any objects from OcalApi to evaluate, so you have to choose an object on your own. To choose an object simply click on it.")

        elif setup.feedback_mode == "hybrid":
            messages.info(request,
                          "Feedback mode for your experiment is 'hybrid'. This means you will receive object queries from OcalApi but you don't have to give feedback to this object. You can choose other objects simply by clicking on them.")

        iteration = Iteration.objects.filter(session_id=session_id).latest('iteration_order')
        iteration_id = iteration.id
        experiment_info = self._session_service.get_experiment_info(session_id)

        obj_id = experiment_info['ocal_query_id']
        ocal_selection = experiment_info['ocal_query_id']

        asked_before = False
        if 'selected_obj_id' in kwargs:
            if setup.feedback_mode == "system":
                messages.warning(request, "You can't select an object while feedback mode is set to 'system'")
                return redirect("/userapp/" + str(kwargs['pk']) + "/experiment/session=" + str(session_id))

            asked_before = SessionService.check_asked_object(session_id, kwargs['selected_obj_id'])
            if asked_before:
                messages.warning(request,
                                 "You can't give feedback to the same object more than one time! You've been redirected to the initial asked object")
                return redirect("/userapp/" + str(kwargs['pk']) + "/experiment/session=" + str(session_id))
            else:
                selected_obj_id = kwargs["selected_obj_id"]
                ocal_selection = obj_id
                obj_id = selected_obj_id
                experiment_info["selected_obj_id"] = obj_id
                experiment_info["ocal_prediction"] = IterationService.get_ocal_prediction_of_selected_obj(iteration_id,
                                                                                                          obj_id)

        default_subspace_id = list(experiment_info["subspaces_ordered"])[0]

        visualization_content = self._iteration_service.get_classifier_results_visualization(iteration_id,
                                                                                             default_subspace_id,
                                                                                             obj_id, ocal_selection)
        graph = visualization_content[0]
        figid = visualization_content[3]
        tooltip_content = visualization_content[4]
        subspace_id = visualization_content[5]

        if obj_id is not None and not asked_before:
            features = visualization_content[2]
            if setup.feature_data_visible == "Yes":
                values = visualization_content[1][obj_id]
            else:
                values = visualization_content[1]
            object_values = zip(features, values)

            image_path = "/../" + self.get_image(obj_id, session.setup_id.dataset_id)

            context = {
                'experiment_info': experiment_info,
                'graph': [graph],
                'setup': setup,
                'iteration_id': iteration_id,
                'features': features,
                'values': values,
                'object_values': object_values,
                'figid': figid,
                'image_path': image_path,
                'tooltip_content': tooltip_content,
                'subspace_id': subspace_id
            }

        else:
            context = {
                'experiment_info': experiment_info,
                'graph': [graph],
                'setup': setup,
                'iteration_id': iteration_id,
                'figid': figid,
                'tooltip_content': tooltip_content,
                'subspace_id': subspace_id
            }

        return render(request, "experiment.html", context)

    def post(self, request, pk, sessionpk, *args, **kwargs):
        """
        Handles the next and back buttons of the view that produce a POST request
        """
        iteration = Iteration.objects.filter(session_id=sessionpk).latest('iteration_order')
        iteration_id = iteration.id
        setup = iteration.session_id.setup_id
        obj_id = iteration.ocal_query_id

        user_feedback = request.POST.get("user_feedback")
        finished_message = "You successfully finished your experiment. Thank you for your contribution!"
        if request.POST.get('action') == "Next" or request.POST.get('action') == "Finish":
            if setup.feedback_mode != "system":
                if 'selected_obj_id' in kwargs:
                    obj_id = kwargs['selected_obj_id']

                if obj_id is not None:
                    result = self._iteration_service.submit_iteration(iteration_id, user_feedback, obj_id)
                    if result != "success":
                        message = "Session " + str(sessionpk) + ": "
                        message += result + " \n Please report this to the administrator"
                        messages.warning(request, message)
                        return redirect("/userapp/" + str(pk) + "/invitations")
                else:
                    messages.warning(request, "No object selected.")

                if request.POST.get('action') == "Finish":
                    session = iteration.session_id
                    session.status = "finished"
                    session.save()
                    messages.success(request, finished_message)
                    return redirect("/userapp/" + "finished_experiments/" + str(sessionpk))

                else:
                    return redirect("/userapp/" + str(pk) + "/experiment/session=" + str(sessionpk))

            elif setup.feedback_mode == "system":
                if 'selected_obj_id' in kwargs:
                    selected_obj_id = kwargs['selected_obj_id']
                    if selected_obj_id != iteration.ocal_query_id:
                        messages.warning(request,
                                         'This experiment has the feedback mode "System". You must give your feedback to the object which has been chosen by OcalApi. You have been redirected to that object.')
                        return redirect(
                            "/userapp/" + str(pk) + "/experiment/session=" + str(sessionpk) + "/obj=" + str(obj_id))

                    elif selected_obj_id == iteration.ocal_query_id:
                        result = self._iteration_service.submit_iteration(iteration_id, user_feedback, obj_id)
                        if result != "success":
                            message = "Session " + str(sessionpk) + ": "
                            message += result + " \n Please report this to the administrator"
                            messages.warning(request, message)
                            return redirect("/userapp/" + str(pk) + "/invitations")

                        if request.POST.get('action') == "Finish":
                            session = iteration.session_id
                            session.status = "finished"
                            session.save()
                            messages.success(request, finished_message)
                            return redirect("/userapp/" + "finished_experiments/" + str(sessionpk))

                        else:
                            return redirect("/userapp/" + str(pk) + "/experiment/session=" + str(sessionpk))

                else:
                    result = self._iteration_service.submit_iteration(iteration_id, user_feedback, obj_id)
                    if result != "success":
                        message = "Session " + str(sessionpk) + ": "
                        message += result + " \n Please report this to the administrator"
                        messages.warning(request, message)
                        return redirect("/userapp/" + str(pk) + "/invitations")

                    if request.POST.get('action') == "Finish":
                        session = iteration.session_id
                        session.status = "finished"
                        session.save()
                        messages.success(request, finished_message)
                        return redirect("/userapp/" + "finished_experiments/" + str(sessionpk))

                    else:
                        return redirect("/userapp/" + str(pk) + "/experiment/session=" + str(sessionpk))

        elif request.POST.get('action') == "Back":
            self._iteration_service.delete_iteration(iteration_id)
            msg = "The algorithms used are sequential. Therefore, the response to the current" \
                  " iteration is reset to maintain consistency."
            messages.warning(request, msg)
            return redirect("/userapp/" + str(pk) + "/experiment/session=" + str(sessionpk))

        else:
            return redirect("/userapp/" + str(pk) + "/experiment/session=" + str(sessionpk))

    def get_image(self, object_id, dataset):
        """
        Gets the raw data visualization image path
        :param object_id: to get the visualization of
        :param dataset: which has the given object
        :return: image path
        """
        image_path = SessionService().get_raw_data_visualization(dataset, object_id)
        return image_path


class LoadSubspaceVisualizationAjaxView(View):
    """
    View to handle asynchronous ajax requests to load a new subspace visualization to template.
    """
    template_name = "subspace_visualization.html"
    _iteration_service = IterationService()
    _session_service = SessionService()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoadSubspaceVisualizationAjaxView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Prepares the requested subspace visualization and renders to template.
        """
        iteration_id = request.POST.get("iteration_id")
        subspace_id = request.POST.get("subspace_id")
        session_id = Iteration.objects.get(id=iteration_id).session_id_id

        experiment_info = self._session_service.get_experiment_info(session_id)
        obj_id = experiment_info['ocal_query_id']
        ocal_selection = experiment_info['ocal_query_id']

        if request.POST.get("selected_obj_id") != '':
            obj_id = int(request.POST.get("selected_obj_id"))

        visualization_content = self._iteration_service.get_classifier_results_visualization(iteration_id, subspace_id,
                                                                                             obj_id, ocal_selection)

        graph = visualization_content[0]
        # values = visualization_content[1][ocal_query_id]
        features = visualization_content[2]
        figid = visualization_content[3]
        tooltip_content = visualization_content[4]
        subspace_id = visualization_content[5]



        context = {
            'graph': [graph],
            'features': features,
            'figid': figid,
            'tooltip_content': tooltip_content,
            'subspace_id': subspace_id,
            'iteration_id': iteration_id,
        }

        return render(request, self.template_name, context)


class AbortExperimentView(DeleteView):
    """
        View of the confirmation page for abandoning the experiment.
    """
    model = Session
    template_name = 'experiment_delete.html'
    success_url = reverse_lazy('home')
    success_message = "Experiment was aborted successfully!"

    def delete(self, request, *args, **kwargs):
        """
        Overrides to not delete the session but set its status to not completed instead
        """
        session = self.get_object()
        _session_service = SessionService()
        _session_service.set_session_status(session, "not_completed")
        messages.success(self.request, self.success_message)
        return redirect(reverse_lazy('home'))


class UserStatsReceiverView(View):
    """
    View for receiving and processing user stats.
    """
    _user_stats_service = UserStatsService()

    def post(self, request):
        """
        Saves duration stats to the system.
        """
        # if (record time spent on subspace)  #ajax request not implemented yet

        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        duration = data["duration"]
        subspaces = data["subspaces"]
        iteration_id = data["iteration_id"]

        self._user_stats_service.update_iteration_duration(duration, iteration_id)

        for subspace in subspaces:
            subspace_id = int(subspace)
            duration = subspaces.get(subspace)
            self._user_stats_service.update_subspace_user_interaction_stats(subspace_id, iteration_id, duration)

        if data["selected_obj"] != "":
            dataset = Iteration.objects.get(id=iteration_id).session_id.setup_id.dataset_id
            IterationService.delete_temp_image(dataset, data["selected_obj"])

        return HttpResponse()

    """
    View that represents a list of sessions.
    """


class UserSessionListView(ListView):
    """
    View for finished / accepted / not_completed sessions pages of the user.
    """
    model = Session
    template_name = 'user_finished_sessions_list.html'
    context_object_name = 'sessions'
    paginate_by = 20

    def get_queryset(self):
        """
            Overrides the method to get the list of finished sessions of the selected setup by
            calling the _session_service method get_finished_sessions_of_setup.
        """
        session_service = SessionService()
        finished_sessions = session_service.filter_sessions_by_status(self.kwargs['pk'], "finished")
        accepted_sessions = session_service.filter_sessions_by_status(self.kwargs['pk'], "accepted")
        not_completed_sessions = session_service.filter_sessions_by_status(self.kwargs['pk'], "not_completed")
        return list(chain(finished_sessions, accepted_sessions, not_completed_sessions))


class UserSessionDetailView(DetailView):
    """
        View that shows all the details of selected finished session.
    """
    model = Session
    template_name = 'user_session_detail.html'
    context_object_name = 'session'

    def get(self, request, *args, **kwargs):
        global session
        if "pk" in kwargs:
            if Session.objects.filter(id=kwargs["pk"]).count() > 0:
                session = Session.objects.get(id=kwargs["pk"])
                context = {"session": session}
            else:
                messages.warning(request, "No session with id " + str(kwargs["pk"]) + " is found")
                return redirect(reverse_lazy('home'))

        if session.user_id != request.user:
            messages.warning(request, "Permission denied")
            return redirect(reverse_lazy('home'))
        else:
            return render(request, self.template_name, context)
