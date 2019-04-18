import re

import requests
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from codehighp.settings.debug import GIT_SERVICE_URL
from compete.models import Problem, ProblemPermission
from problemsetting.forms import AddProblemDeveloperForm, ProblemNameForm, ProblemCreateForm
from problemsetting.tasks import update_problem_from_git, delete_problem
from users.models import CustomUser


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
                requests.post(GIT_SERVICE_URL + '/DelKey', headers=dict(key=key), auth=('git', settings.GIT_SERVICE_PASSWORD))
        if 'add_key' in request.POST:
            key_name = request.POST.get('key_name')
            key = request.POST.get('key')
            if re.match(r'^[a-zA-Z0-9\-]+$', key_name) and type(key) == str:
                key = key.strip().replace('\n', ' ')
                requests.post(GIT_SERVICE_URL + '/AddKey',
                              headers=dict(username=self.request.user.username, name=key_name, key=key),
                              auth=('git', settings.GIT_SERVICE_PASSWORD))
        return HttpResponseRedirect(request.path_info)

    def get_keys(self):
        keys = requests.get(GIT_SERVICE_URL + '/GetUserKeys',
                            headers=dict(username=self.request.user.username),
                            auth=('git', settings.GIT_SERVICE_PASSWORD)).json()
        return keys

    def get_context_data(self, **kwargs):
        context = super(ManageSSHKeysView, self).get_context_data(**kwargs)

        context['keys'] = self.get_keys()
        return context


class MainView(ProblemsetterAccessRequired, FormView):
    template_name = 'problemsetting/main.html'
    form_class = ProblemCreateForm

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        perms = {x.problem_id: x for x in ProblemPermission.objects.filter(user_id=self.request.user.id).all()}
        problems = Problem.objects.filter(id__in=list(perms)).order_by('-id').all()
        for prob in problems:
            prob.acc = perms[prob.id].access
        context['problems'] = problems
        return context

    def form_valid(self, form):
        form.save(self.request.user.id)
        return HttpResponseRedirect(self.request.path_info)


class ProblemManageView(ProblemsetterAccessRequired, FormView):
    template_name = 'problemsetting/problem.html'
    form_class = AddProblemDeveloperForm

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
        if any(act in request.POST for act in ['revoke', 'read', 'write']) and self.permission == ProblemPermission.OWNER:
            user = get_object_or_404(CustomUser, pk=request.POST.get('user_id'))
            perm = get_object_or_404(ProblemPermission, user_id=user.id, problem_id=self.problem.id)
            if perm.access != ProblemPermission.OWNER:
                if 'revoke' in request.POST:
                    perm.delete()
                elif 'read' in request.POST:
                    perm.access = ProblemPermission.READ
                    perm.save()
                elif 'write' in request.POST:
                    perm.access = ProblemPermission.WRITE
                    perm.save()
                self.problem.update_git_permissions()
        if 'rename' in request.POST:
            form = ProblemNameForm(request.POST, instance=self.problem)
            if form.is_valid():
                form.save()
        if 'delete' in request.POST:
            delete_problem.delay(self.problem.internal_name)
            self.problem.delete()
            return HttpResponseRedirect(reverse('problemsetting'))
        if 'add_developer' in request.POST and self.permission == ProblemPermission.OWNER:
            return super(ProblemManageView, self).post(request, *args, **kwargs)
        return HttpResponseRedirect(request.path_info)

    def get_context_data(self, **kwargs):
        context = super(ProblemManageView, self).get_context_data(**kwargs)
        context['problem'] = self.problem
        context['permissions'] = self.permissions
        context['is_owner'] = self.permission == ProblemPermission.OWNER
        context['rename_form'] = ProblemNameForm(initial=dict(name=self.problem.name))
        return context

    def get_form_kwargs(self):
        kwargs = super(ProblemManageView, self).get_form_kwargs()
        kwargs['prob_id'] = self.problem.id
        return kwargs

    def form_valid(self, form):
        form.add_developer()
        self.problem.update_git_permissions()
        return HttpResponseRedirect(self.request.path_info)
