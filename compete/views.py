import base64

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, FormView, TemplateView
from django.views.generic.detail import SingleObjectMixin

from compete.forms import RunSubmitForm, ContestRegistrationForm
from compete.invoke import VERDICTS
from compete.models import Problem, Run, Contest, ContestRegistration, UserProblemStatus


class ContestListView(TemplateView):
    template_name = 'compete/contest_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ContestListView, self).get_context_data(object_list=object_list, **kwargs)
        contests = Contest.get_visible(Contest.objects
            .prefetch_related('authors')
            .annotate(num_participants=Count('participants', filter=Q(
                            contestregistration__status=ContestRegistration.REGISTERED),
                            distinct=True))
            .order_by('-id'), self.request.user.id)
        if self.request.user.is_authenticated:
            regs = ContestRegistration.objects.filter(user_id=self.request.user.id)
            dregs = {i.contest_id: i for i in regs}
            for contest in contests:
                if contest.id in dregs:
                    contest.reg = dregs[contest.id]
        context['contest_list'] = contests
        return context


class ContestRegistrationView(LoginRequiredMixin, FormView):
    template_name = 'compete/contest_registration.html'
    form_class = ContestRegistrationForm

    def get_context_data(self, **kwargs):
        context = super(ContestRegistrationView, self).get_context_data(**kwargs)
        contest = get_object_or_404(Contest, pk=self.kwargs.get('pk'))
        if not contest.can_register(self.request.user.id):
            raise PermissionDenied
        context['contest'] = contest
        return context

    def get_initial(self):
        initial = super(ContestRegistrationView, self).get_initial()
        initial['contest_id'] = self.kwargs.get('pk')
        return initial

    def get_form_kwargs(self):
        kwargs = super(ContestRegistrationView, self).get_form_kwargs()
        contest = get_object_or_404(Contest, pk=self.kwargs.get('pk'))
        kwargs['reg'] = contest.registration
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.register()
        return redirect(reverse('contest_list'))


class ContestView(TemplateView):
    template_name = 'compete/contest.html'

    def get_context_data(self, **kwargs):
        context = super(ContestView, self).get_context_data(**kwargs)
        contest = get_object_or_404(Contest, pk=self.kwargs.get('pk'))
        reg = contest.ensure_can_access(self.request.user.id)
        problems = contest.problem_set.order_by('short_name').all()
        problem_statuses = UserProblemStatus.objects.filter(user_id=self.request.user.id, problem__in=problems).all()
        problem_statuses = {i.problem_id: i for i in problem_statuses}
        for prob in problems:
            status = problem_statuses.get(prob.id)
            if status:
                prob.attempted = True
                prob.user_score = round(prob.score * status.score / Run.SCORE_DIVISOR)
                prob.user_score2 = round(prob.score * status.score2 / Run.SCORE_DIVISOR)

                if prob.user_score <= 0:
                    prob.css_class = "failed-attempt"
                elif prob.user_score >= prob.score:
                    prob.css_class = "successful-attempt"
                else:
                    prob.css_class = "partial-attempt"
            else:
                prob.css_class = ""

        context['contest'] = contest
        context['problems'] = problems
        if reg:
            context['registration'] = reg
        return context


class ProblemListView(ListView):
    model = Problem
    template_name = 'compete/problem_list.html'

    def get_queryset(self):
        queryset = Problem.objects.filter(
            visibility=Problem.VISIBLE_EVERYONE
        ).order_by('-id')
        return queryset


class ContestRunsView(LoginRequiredMixin, ListView):
    model = Run
    template_name = 'compete/contest_runs.html'
    paginate_by = settings.RUNS_ON_PROBLEM_PAGE

    def get_context_data(self, **kwargs):
        context = super(ContestRunsView, self).get_context_data(**kwargs)
        contest = get_object_or_404(Contest, pk=self.kwargs.get('pk'))
        context['contest'] = contest
        reg = contest.ensure_can_access(self.request.user.id)
        context['registration'] = reg
        flavor_cache = dict()
        for run in context['run_list']:
            if run.problem_id not in flavor_cache:
                flavor_cache[run.problem_id] = run.problem.config['flavor'].split('.')[0]
            run.flavor = flavor_cache[run.problem_id]
        return context

    def get_queryset(self):
        queryset = Run.objects.filter(
            problem__contest_id=self.kwargs.get('pk'), user=self.request.user)\
            .order_by('-id')\
            .select_related('user', 'problem')
        return queryset


class ProblemRunsView(LoginRequiredMixin, ListView):
    model = Run
    template_name = 'compete/problem_runs.html'
    paginate_by = settings.RUNS_ON_PROBLEM_PAGE

    def get_context_data(self, **kwargs):
        context = super(ProblemRunsView, self).get_context_data(**kwargs)
        problem = get_object_or_404(Problem, pk=self.kwargs.get('pk'))
        if not problem.is_visible(self.request.user.id):
            raise PermissionDenied
        for run in context['run_list']:
            run.flavor = problem.config['flavor'].split('.')[0]
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

    def post(self, request, *args, **kwargs):
        problem = get_object_or_404(Problem, pk=self.kwargs.get('pk'))
        if not problem.is_visible(self.request.user):
            raise PermissionDenied
        can_submit = False
        if problem.contest_id:
            reg = ContestRegistration.objects.filter(user_id=self.request.user.id, contest_id=problem.contest_id, status=ContestRegistration.REGISTERED)
            if reg.exists():
                can_submit = True
        else:
            can_submit = True
        if not can_submit:
            raise PermissionDenied
        return super(ProblemView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        problem = get_object_or_404(Problem, pk=self.kwargs.get('pk'))
        context['problem'] = problem
        if not problem.is_visible(self.request.user.id):
            raise PermissionDenied
        if problem.contest_id:
            context['contest'] = problem.contest
        if self.request.user.is_authenticated:
            runs = Run.objects.filter(user_id=self.request.user.id, problem=problem) \
                                  .order_by('-id').select_related('user', 'problem')[:settings.RUNS_ON_PROBLEM_PAGE]
            context['runs_truncated'] = (len(runs) == settings.RUNS_ON_PROBLEM_PAGE)
            context['runs'] = runs
            for run in runs:
                run.flavor = problem.config['flavor'].split('.')[0]
            if problem.contest_id:
                reg = list(ContestRegistration.objects.filter(user_id=self.request.user.id, contest_id=problem.contest_id))
                if reg:
                    context['registration'] = reg[0]
                    if reg[0].status == ContestRegistration.REGISTERED:
                        context['can_submit'] = True
            else:
                context['can_submit'] = True
        return context
    
    def get_initial(self):
        initial = super(ProblemView, self).get_initial()
        initial['prob_id'] = self.kwargs.get('pk')
        return initial

    def get_form_kwargs(self):
        problem = get_object_or_404(Problem, pk=self.kwargs.get('pk'))
        kwargs = super(ProblemView, self).get_form_kwargs()
        kwargs['flavor'] = problem.config['flavor']
        return kwargs

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
        context['flavor'] = run.problem.config['flavor'].split('.')[0]
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
