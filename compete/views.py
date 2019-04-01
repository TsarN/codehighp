from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, FormView

from compete.forms import RunSubmitForm
from compete.models import Problem, Run


class ProblemListView(ListView):
    model = Problem
    template_name = 'compete/problem_list.html'


class ProblemRunsView(ListView):
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
            .select_related('user')
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
                                  .order_by('-id').select_related('user')[:settings.RUNS_ON_PROBLEM_PAGE]
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
