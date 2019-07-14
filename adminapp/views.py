from builtins import super

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView

from adminapp.forms import SubspaceFormSetUpdate, SubspaceFormSet, SetupForm, SetupUpdateForm
from adminapp.models import Setup, Dataset, Session, Iteration
from adminapp.services import DatasetService, SetupService, SessionService


class DatasetCreateView(CreateView):
    """
    View to create the dataset objects

    Attributes:
        template_name template to be used
        fields fields to be shown to the user
        model the object to be created
    """
    model = Dataset
    fields = ["name", "description", "type", "feature_file", "raw_file"]
    template_name = 'dataset_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(DatasetCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        response = super(DatasetCreateView, self).form_valid(form)
        self.object = form.save()
        id = self.object.id
        _dataset_service = DatasetService()
        _dataset_service.save_dataset_info(id)
        messages.success(self.request, 'Dataset has been created successfully!')
        return response


class DatasetUpdateView(SuccessMessageMixin, UpdateView):
    """
    View to update the dataset objects

    Attributes:
        template_name template to be used
        fields fields to be shown to the user
        model the object to be created
        success_message message to be returned when dataset is updated
    """
    model = Dataset
    fields = ["name", "description"]
    template_name = "dataset_update.html"
    success_message = 'Dataset was updated successfully!'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(DatasetUpdateView, self).dispatch(*args, **kwargs)


class DatasetListView(ListView):
    """
    View to list the dataset objects

    Attributes:
        template_name template to be used
        model the object to be listed
        paginate_by number of objects on each page
        queryset which objects must be shown
        context_object_name objects to be listed
    """
    model = Dataset
    template_name = 'dataset_list.html'
    context_object_name = 'datasets'
    paginate_by = 20
    queryset = Dataset.objects.all()

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(DatasetListView, self).dispatch(*args, **kwargs)


class DatasetDetailView(DetailView):
    """
    View to show the dataset profile

    Attributes:
       template_name template to be used
       model the object to be created
       context_object_name objects to be shown
    """
    model = Dataset
    template_name = 'dataset_profile.html'
    context_object_name = 'dataset'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(DatasetDetailView, self).dispatch(*args, **kwargs)


class DatasetDeleteView(DeleteView):
    """
    View to delete the dataset objects

    Attributes:
       template_name template to be used
       model the object to be created
       success_url url to be redirected to when success
       success_message message to be shown to when success
    """
    model = Dataset
    template_name = 'dataset_delete.html'
    success_url = reverse_lazy('dataset-list')
    success_message = "Dataset %(name)s was removed successfully!"

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(DatasetDeleteView, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(DatasetDeleteView, self).delete(request, *args, **kwargs)


class SetupCreateView(CreateView):
    """
    View to create the setup objects

    Attributes:
        template_name template to be used
        fields fields to be shown to the user
        model the object to be created
        success_url url to be redirected to when success
    """
    model = Setup
    form_class = SetupForm
    template_name = 'setup_create.html'
    success_url = reverse_lazy('setup-detail')

    def get_context_data(self, **kwargs):
        """
        Overrides the method to get the list of features for the subspace selection.
        :param kwargs:
        :return: list of features for the subspace selection.
        """
        data = super(SetupCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['subspace_formset'] = SubspaceFormSet(self.request.POST)
        else:
            data['subspace_formset'] = SubspaceFormSet()
        return data

    def form_valid(self, form):
        """
        Overrides the method to save the gridpoints data and subspace objects.
        """
        context = self.get_context_data()
        subspace_formset = context['subspace_formset']
        _setup_service = SetupService()
        with transaction.atomic():
            self.object = form.save()
            if subspace_formset.is_valid():
                subspace_formset.instance = self.object
                subspace_formset.save()

        messages.success(self.request, 'Setup ' + self.object.name + ' has been created successfully!')
        return super(SetupCreateView, self).form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(SetupCreateView, self).dispatch(*args, **kwargs)


class SetupUpdateView(SuccessMessageMixin, UpdateView):
    """
    View to update the setup objects

    Attributes:
        template_name template to be used
        model the object to be created
        is_update_view boolean to determine that this is an update view
        success_message message to be shown when success
        success_url url to be redirected to when success
    """
    model = Setup
    form_class = SetupUpdateForm
    is_update_view = True
    template_name = "setup_update.html"
    success_message = 'Setup was updated successfully!'

    success_url = reverse_lazy('setup-detail')

    def get_context_data(self, **kwargs):
        """
        Overrides the method to get the list of features for the subspace selection.
        :return: list of features for the subspace selection.
        """
        data = super(SetupUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['subspace_formset'] = SubspaceFormSetUpdate(self.request.POST, instance=self.get_object())
        else:
            data['subspace_formset'] = SubspaceFormSetUpdate(instance=self.get_object())
        return data

    def form_valid(self, form):
        """
        Overrides the method to save the gridpoints data and subspace objects.
        """
        context = self.get_context_data()
        subspace_formset = context['subspace_formset']
        with transaction.atomic():
            self.object = form.save()
            if subspace_formset.is_valid():
                subspace_formset.instance = self.object
                subspace_formset.save()
        return super(SetupUpdateView, self).form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(SetupUpdateView, self).dispatch(*args, **kwargs)


class SetupListView(ListView):
    """
    View to list the setup objects

    Attributes:
        template_name template to be used
        model the object to be listed
        paginate_by number of objects on each page
        queryset which objects must be shown
        context_object_name objects to be listed
    """
    model = Setup
    template_name = 'setup_list.html'
    context_object_name = 'setups'
    paginate_by = 20
    queryset = Setup.objects.all()

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(SetupListView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        dataset = str(request.GET.get('dataset_id', 'all'))
        self.extra_context = {}
        try:
            if dataset != 'all' and Dataset.objects.filter(id=dataset).count() > 0:
                self.queryset = Setup.objects.filter(dataset_id_id=dataset)
                self.extra_context = {"dataset_obj": Dataset.objects.get(id=dataset)}
        except Exception as e:
            pass
        datasets = set()
        for setup in Setup.objects.all():
            datasets.add(setup.dataset_id)
        self.extra_context["datasets"] = datasets
        return super(SetupListView, self).get(self, request, *args, **kwargs)


class SetupDetailView(SuccessMessageMixin, DetailView):
    """
    View to show the setup profile

    Attributes:
      template_name template to be used
      model the object to be created
      context_object_name objects to be shown
    """
    model = Setup
    template_name = 'setup_profile.html'
    context_object_name = 'setup'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(SetupDetailView, self).dispatch(*args, **kwargs)

    def post(self, request, pk):
        """
         Handles the buttons of the view that produce a POST request:
         - Start Experiment: Calls the _setup_service method set_final.
         - Clone: Calls the _setup_service method clone_setup.
         - Export : Calls _setup_service method export_all
        """
        _setup_service = SetupService()
        setup = self.get_object()

        if request.POST.get("action") == "start_experiment":
            success_msg = _setup_service.set_final(setup.id)
            if success_msg == "success":
                messages.success(self.request,
                                 'Setup ' + setup.name + ' has been started.'
                                                         ' Now you can invite participants from Create Experiment Page')

                return redirect("/adminapp/" + "experiments/new/" + "setup=" + str(setup.id))
            else:
                messages.warning(self.request, success_msg)
                return HttpResponseRedirect(setup.get_absolute_url())

        elif request.POST.get("action") == "clone":
            clone = _setup_service.clone_setup(setup.id)
            messages.success(self.request,
                             'Setup ' + setup.name + ' has been successfully cloned.'
                                                     ' Please do not forget to change its name for consistency.')
            return HttpResponseRedirect(clone.get_absolute_url())

        elif request.POST.get("action") == "send_invitation":
            return redirect("/adminapp/" + "experiments/new/" + "setup=" + str(setup.id))

        elif request.POST.get('action') == "export_all":
            response = HttpResponse(_setup_service.export_all(setup.id), content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=result_setup' + str(setup.id) + '.json'
            return response


class SetupDeleteView(DeleteView):
    """
    View to delete the setup objects

    Attributes:
       template_name template to be used
       model the object to be created
       success_url url to be redirected to when success
       success_message message to be shown to when success
    """
    model = Setup
    template_name = 'setup_delete.html'
    success_url = reverse_lazy('setup-list')
    success_message = "Setup %(name)s was removed successfully!"

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(SetupDeleteView, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(SetupDeleteView, self).delete(request, *args, **kwargs)


class SetupInviteUsersView(ListView):
    """
    View to create the session objects

    Attributes:
        template_name template to be used
        model the object to be created
        paginate_by number of users to be shown
        queryset which users should be shown
        context_object_name objects to be listed
    """

    model = User
    template_name = 'session_create.html'
    context_object_name = 'users'
    paginate_by = 20
    queryset = Setup.objects.all()

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(SetupInviteUsersView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        users = User.objects.filter(is_superuser=False)
        setups = Setup.objects.filter(status="final")
        context = {
            'users': users,
            'setups': setups,
        }
        if 'setuppk' in kwargs:
            context['selected_setup'] = Setup.objects.get(id=kwargs['setuppk'])
        return render(request, 'session_create.html', context)

    def post(self, request, *args, **kwargs):
        session_service = SessionService()
        setup_id = request.POST['setup_id']
        users = request.POST.getlist('user_ids')
        users_list = []
        for user in users:
            users_list.append(User.objects.get(id=user).username)
        users_list_string = ', '.join(users_list)
        success_message = "Invitation(s) has been successfully sent to: " + users_list_string

        for user in users:
            user_id = user
            session_service.create_inactive_session_from_invitation(setup_id, user_id)

        messages.success(self.request, success_message)
        return HttpResponseRedirect(reverse('session-list'))


class SetupFinishedSessionsView(ListView):
    """
    View to show the session objects with finished status

    Attributes:
        template_name template to be used
        model the object to be shown
        paginate_by number of users to be shown
        context_object_name objects to be listed
    """
    model = Session
    template_name = 'finished_sessions_list.html'
    context_object_name = 'sessions'
    paginate_by = 20

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(SetupFinishedSessionsView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        """
        Overrides the method to get the list of finished sessions of the selected setup by
        calling the _session_service method get_finished_sessions_of_setup.
        :return: finished_sessions
        """
        session_service = SessionService()
        setup_id = self.kwargs['pk']
        finished_sessions = session_service.get_finished_sessions_for_setup(setup_id)
        return finished_sessions


class SessionListView(ListView):
    """
    View to show all session objects

    Attributes:
        template_name template to be used
        model the object to be shown
        paginate_by number of users to be shown
        context_object_name objects to be listed
        queryset which objects to be listed
    """
    model = Session
    template_name = 'session_list.html'
    context_object_name = 'sessions'
    paginate_by = 20
    queryset = Session.objects.all()

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(SessionListView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        status = request.GET.get('status', 'all')
        if status != 'all':
            self.queryset = Session.objects.filter(status=status)
            self.extra_context = {"selected_status": status}
        return super(SessionListView, self).get(self, request, *args, **kwargs)


class SessionDetailView(DetailView):
    """
    View to show the session profile

    Attributes:
      template_name template to be used
      model the object to be created
      context_object_name objects to be shown
    """
    model = Session
    template_name = 'session_detail.html'
    context_object_name = 'session'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(SessionDetailView, self).dispatch(*args, **kwargs)

    def post(self, request, **kwargs):
        """
        Handles the buttons of the view that produce a POST request:
          Accept
          Export
        """
        session_service = SessionService()
        session_id = self.get_object().id  # get the session id from the request

        if request.POST.get('action') == "accept":
            session_service.set_accepted(session_id)
            return HttpResponseRedirect(self.get_object().get_absolute_url())

        elif request.POST.get('action') == "export":
            response = HttpResponse(session_service.export_session_results(session_id), content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=result_session' + str(session_id) + '.json'
            return response


class SessionDeleteView(DeleteView):
    """
    View to delete the session objects

    Attributes:
       template_name template to be used
       model the object to be created
       success_url url to be redirected to when success
       success_message message to be shown to when success
    """
    model = Session
    template_name = 'session_delete.html'
    success_url = reverse_lazy('session-list')
    success_message = "Session was removed successfully!"

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(SessionDeleteView, self).dispatch(*args, **kwargs)
