import re

import requests
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import FormView, TemplateView

from codehighp.settings.debug import GIT_SERVICE_URL


class ProblemsetterAccessRequired(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.is_problemsetter


class ManageSSHKeysView(ProblemsetterAccessRequired, TemplateView):
    template_name = 'problemsetting/ssh_keys.html'

    def post(self, request, *args, **kwargs):
        if 'delete_key' in request.POST:
            key = request.POST.get('key_name')
            if key in self.get_keys():
                requests.post(GIT_SERVICE_URL + '/DelKey', headers=dict(key=key))
        if 'add_key' in request.POST:
            key_name = request.POST.get('key_name')
            key = request.POST.get('key')
            if re.match(r'^[a-zA-Z0-9\-]+$', key_name):
                requests.post(GIT_SERVICE_URL + '/AddKey', headers=dict(username=self.request.user.username, name=key_name, key=key))
        return HttpResponseRedirect(request.path_info)

    def get_keys(self):
        keys = requests.get(GIT_SERVICE_URL + '/GetUserKeys', headers=dict(username=self.request.user.username)).json()
        return keys

    def get_context_data(self, **kwargs):
        context = super(ManageSSHKeysView, self).get_context_data(**kwargs)

        context['keys'] = self.get_keys()
        return context
