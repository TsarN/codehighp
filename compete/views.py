from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, FormView, TemplateView

from compete.forms import RunSubmitForm
from compete.invoke import VERDICTS
from compete.models import Problem, Run


class ProblemListView(ListView):
    model = Problem
    template_name = 'compete/problem_list.html'


class ProblemRunsView(LoginRequiredMixin, ListView):
    login_url = '/users/login'
    model = Run
    template_name = 'compete/problem_runs.html'
    paginate_by = settings.RUNS_ON_PROBLEM_PAGE

    def get_context_data(self, **kwargs):
        context = super(ProblemRunsView, self).get_context_data(**kwargs)
        problem = get_object_or_404(Problem, pk=self.kwargs.get('pk'))
        context['problem'] = problem
        return context

    def get_queryset(self):
        queryset = Run.objects.filter(
            problem_id=self.kwargs.get('pk'), user=self.request.user)\
            .order_by('-id')\
            .select_related('user', 'problem')
        return queryset


class ProblemView(FormView):
    template_name = 'compete/problem.html'
    form_class = RunSubmitForm

    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        problem = get_object_or_404(Problem, pk=self.kwargs.get('pk'))
        context['problem'] = problem
        if self.request.user.is_authenticated:
            runs = Run.objects.filter(user=self.request.user, problem=problem) \
                                  .order_by('-id').select_related('user', 'problem')[:settings.RUNS_ON_PROBLEM_PAGE]
            context['runs_truncated'] = (len(runs) == settings.RUNS_ON_PROBLEM_PAGE)
            context['runs'] = runs
        return context
    
    def get_initial(self):
        initial = super(ProblemView, self).get_initial()
        initial['prob_id'] = self.kwargs.get('pk')
        return initial

    def form_valid(self, form):
        form.submit_run(self.request.user)
        return redirect(self.request.get_full_path())


class RunView(TemplateView):
    template_name = 'compete/run.html'

    def get_context_data(self, **kwargs):
        context = super(RunView, self).get_context_data(**kwargs)
        run = get_object_or_404(Run, pk=self.kwargs.get('pk'))
        context['run'] = run
        context['runs'] = [run]
        log = run.read_log()

        try:
            context['compile_log'] = log[b'compile'].decode()
        except:
            pass

        tests = []
        group = 0
        while group in log:
            test = 0
            glog = log[group]
            tests.append(dict(tests=[], score=glog[b'score'] / Run.SCORE_DIVISOR))
            while test in glog:
                d = dict({k.decode(): v for k, v in glog[test].items()})
                d['verdict'] = VERDICTS[d['verdict'].decode()]
                tests[group]['tests'].append(d)
                test += 1
            group += 1
        context['tests'] = tests

        return context
