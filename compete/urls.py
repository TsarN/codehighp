from django.urls import path

from . import views

urlpatterns = [
    path('contests/', views.ContestListView.as_view(), name='contest_list'),
    path('contest/<int:pk>', views.ContestView.as_view(), name='contest'),
    path('contest/<int:pk>/register', views.ContestRegistrationView.as_view(), name='contest_register'),
    path('contest/<int:pk>/registrations', views.ContestRegistrationsView.as_view(), name='contest_registrations'),
    path('contest/<int:pk>/runs', views.ContestRunsView.as_view(), name='contest_runs'),
    path('contest/<int:pk>/scoreboard', views.ContestScoreboardView.as_view(), name='contest_scoreboard'),
    path('problems/', views.ProblemListView.as_view(), name='problem_list'),
    path('problem/<int:pk>', views.ProblemView.as_view(), name='problem'),
    path('problem/<int:pk>/runs', views.ProblemRunsView.as_view(), name='problem_runs'),
    path('run/<int:pk>', views.RunView.as_view(), name='run')
]
