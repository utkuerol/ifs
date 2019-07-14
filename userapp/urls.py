from django.urls import path

from userapp.views import *

urlpatterns = [

    path('<int:pk>/invitations', UserInvitationsListView.as_view(), name="user-sessions-list"),
    path('<int:pk>/ongoing_experiments', UserOngoingSessionsListView.as_view(), name="user-ongoing-sessions-list"),
    path('<int:pk>/experiment/session=<int:sessionpk>', ExperimentView.as_view(),
         name="experiment"),
    path('<int:pk>/experiment/session=<int:sessionpk>/obj=<int:selected_obj_id>', ExperimentView.as_view(),
         name="experiment-with-obj"),
    path('experiment/<int:pk>/delete', AbortExperimentView.as_view(), name="delete-experiment"),
    path('ajax/subspacevis', LoadSubspaceVisualizationAjaxView.as_view(), name="subspacevis"),
    path('ajax/duration', UserStatsReceiverView.as_view(), name="duration"),

    path('<int:pk>/participated_experiments', UserSessionListView.as_view(), name="user-sessions-list"),
    path('finished_experiments/<int:pk>', UserSessionDetailView.as_view(), name="finished-session")
]
