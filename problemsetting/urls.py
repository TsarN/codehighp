from django.urls import path

from . import views

urlpatterns = [
    path('', views.MainView.as_view(), name='problemsetting'),
    path('ssh_keys/', views.ManageSSHKeysView.as_view(), name='ssh_keys'),
    path('problem/<int:pk>', views.ProblemManageView.as_view(), name='problem_manage'),
]
