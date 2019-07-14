from django.urls import path
from adminapp.views import *

urlpatterns = [
    path('setups/new', SetupCreateView.as_view(), name='new-setup'),
    path('setups/', SetupListView.as_view(), name='setup-list'),
    path('setups/<int:pk>/', SetupDetailView.as_view(), name='setup-detail'),
    path('setups/<int:pk>/update/', SetupUpdateView.as_view(), name='setup-update'),
    path('setups/<int:pk>/delete/', SetupDeleteView.as_view(), name='setup-delete'),
    path('setups/<int:pk>/finishedsessions', SetupFinishedSessionsView.as_view(), name='setup-finished-sessions'),

    path('datasets/new', DatasetCreateView.as_view(), name='new-dataset'),
    path('datasets/', DatasetListView.as_view(), name='dataset-list'),
    path('datasets/<int:pk>/', DatasetDetailView.as_view(), name='dataset-detail'),
    path('datasets/<int:pk>/update/', DatasetUpdateView.as_view(), name='dataset-update'),
    path('datasets/<int:pk>/delete/', DatasetDeleteView.as_view(), name='dataset-delete'),

    path('experiments/new', SetupInviteUsersView.as_view(), name='session-create'),
    path('experiments/new/setup=<int:setuppk>', SetupInviteUsersView.as_view(), name='session-create'),
    path('experiments/', SessionListView.as_view(), name='session-list'),
    path('experiments/<int:pk>/', SessionDetailView.as_view(), name='session-detail'),
    path('experiments/<int:pk>/delete', SessionDeleteView.as_view(), name='session-delete'),

]
