from django.urls import path

from compete.views import ProblemListView, ProblemView, ProblemRunsView, RunView, ContestListView
from . import views

urlpatterns = [
    path('contests/', ContestListView.as_view(), name='contest_list'),
    path('problems/', ProblemListView.as_view(), name='problem_list'),
    path('problem/<int:pk>', ProblemView.as_view(), name='problem'),
    path('problem/<int:pk>/runs', ProblemRunsView.as_view(), name='problem_runs'),
    path('run/<int:pk>', RunView.as_view(), name='run')
]