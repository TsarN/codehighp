from django.urls import path

from blog.views import IndexView
from . import views

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('privacy', views.PrivacyPolicyView.as_view(), name='privacy'),
    path('help', views.HelpView.as_view(), name='help'),
    path('help/<path:page>', views.HelpView.as_view(), name='help')
]
