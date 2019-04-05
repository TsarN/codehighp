import base64

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, FormView, TemplateView
from django.views.generic.detail import SingleObjectMixin

from compete.forms import RunSubmitForm
from compete.invoke import VERDICTS
from compete.models import Problem, Run, Contest


class ContestListView(ListView):
    model = Contest
    template_name = 'compete/contest_list.html'

    def get_queryset(self):
        return Contest.objects.prefetch_related('authors')


class ProblemListView(ListView):
    model = Problem
    template_name = 'compete/problem_list.html'


class ProblemRunsView(LoginRequiredMixin, ListView):
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


class RunView(SingleObjectMixin, UserPassesTestMixin, TemplateView):
    template_name = 'compete/run.html'
    model = Run

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(RunView, self).dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.object.accessible_by(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(RunView, self).get_context_data(**kwargs)
        run = self.object
        context['run'] = run
        context['runs'] = [run]
        log = run.read_log()

        try:
            with open(run.src_path, 'rb') as f:
                src = f.read()
            try:
                src = src.decode()
            except UnicodeDecodeError:
                src = '[Source is base64 encoded]\n' + base64.b64encode(src).decode()
        except:
            src = None

        context['src'] = src

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
                for field in ('input', 'output', 'answer'):
                    if field not in d:
                        d[field] = '[too long]'
                    elif not d[field]:
                        d[field] = '[none]'
                d['verdict'] = VERDICTS[d['verdict'].decode()]
                tests[group]['tests'].append(d)
                test += 1
            group += 1
        context['tests'] = tests

        return context
