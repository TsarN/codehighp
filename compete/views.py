from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, TemplateView

from compete.models import Problem, Run


class ProblemListView(ListView):
    model = Problem
    template_name = 'compete/problem_list.html'


class ProblemView(TemplateView):
    template_name = 'compete/problem.html'

    def get_context_data(self, **kwargs):
        context = super(ProblemView, self).get_context_data(**kwargs)
        problem = get_object_or_404(Problem, pk=kwargs.get('pk'))
        context['problem'] = problem
        if self.request.user.is_authenticated:
            context['runs'] = Run.objects.filter(user=self.request.user, problem=problem)
        return context
