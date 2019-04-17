from django.urls import path

from . import views

urlpatterns = [
    path('ssh_keys/', views.ManageSSHKeysView.as_view(), name='ssh_keys')
]
