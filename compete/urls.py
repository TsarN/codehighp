from django.urls import path

from compete.views import ProblemListView, ProblemView, ProblemRunsView, RunView, ContestListView, \
    ContestRegistrationView, ContestView, ContestRunsView
from . import views

urlpatterns = [
    path('contests/', ContestListView.as_view(), name='contest_list'),
    path('contest/<int:pk>', ContestView.as_view(), name='contest'),
    path('contest/<int:pk>/register', ContestRegistrationView.as_view(), name='contest_register'),
    path('contest/<int:pk>/runs', ContestRunsView.as_view(), name='contest_runs'),
    path('problems/', ProblemListView.as_view(), name='problem_list'),
    path('problem/<int:pk>', ProblemView.as_view(), name='problem'),
    path('problem/<int:pk>/runs', ProblemRunsView.as_view(), name='problem_runs'),
    path('run/<int:pk>', RunView.as_view(), name='run')
]