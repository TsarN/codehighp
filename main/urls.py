from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('help', views.HelpView.as_view(), name='help'),
    path('help/<path:page>', views.HelpView.as_view(), name='help')
]