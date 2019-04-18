import requests
from celery import shared_task
from django.conf import settings

from compete.models import Problem


@shared_task(queue='manager')
def update_problem_from_git(problem_id):
    try:
        problem = Problem.objects.get(pk=problem_id)
    except:
        return
    for invoker in settings.INVOKERS:
        res = requests.post(invoker['watchdog'] + '/UpdateProblem',
                            headers=dict(problem=problem.internal_name)).text
        if res:
            problem.error = res
            break
    else:
        problem.error = ""
    problem.save()
