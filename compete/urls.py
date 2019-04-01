from django.urls import path

from compete.views import ProblemListView, ProblemView, ProblemRunsView
from . import views

urlpatterns = [
    path('problems/', ProblemListView.as_view(), name='problem_list'),
    path('problem/<int:pk>', ProblemView.as_view(), name='problem'),
    path('problem/<int:pk>/runs', ProblemRunsView.as_view(), name='problem_runs')
]