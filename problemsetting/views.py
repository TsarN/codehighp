import re

import requests
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, TemplateView

from codehighp.settings.debug import GIT_SERVICE_URL
from compete.models import Problem, ProblemPermission
from problemsetting.tasks import update_problem_from_git


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


class MainView(ProblemsetterAccessRequired, TemplateView):
    template_name = 'problemsetting/main.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        perms = {x.problem_id: x for x in ProblemPermission.objects.filter(user_id=self.request.user.id).all()}
        problems = Problem.objects.filter(id__in=list(perms)).order_by('-id').all()
        for prob in problems:
            prob.acc = perms[prob.id].access
        context['problems'] = problems
        return context


class ProblemManageView(ProblemsetterAccessRequired, TemplateView):
    template_name = 'problemsetting/problem.html'

    def dispatch(self, request, *args, **kwargs):
        self.problem = get_object_or_404(Problem, pk=kwargs.get('pk'))
        self.permission = self.problem.get_access(self.request.user.id)
        if self.permission not in [ProblemPermission.WRITE, ProblemPermission.OWNER]:
            raise PermissionDenied
        self.permissions = ProblemPermission.objects\
            .filter(problem_id=self.problem.id)\
            .select_related('user')
        return super(ProblemManageView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if 'update' in request.POST:
            self.problem.error = "Updating... Please wait."
            self.problem.save()
            update_problem_from_git.delay(self.problem.id)
        return HttpResponseRedirect(request.path_info)

    def get_context_data(self, **kwargs):
        context = super(ProblemManageView, self).get_context_data(**kwargs)
        context['problem'] = self.problem
        context['permissions'] = self.permissions
        context['is_owner'] = self.permission == ProblemPermission.OWNER
        return context
