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
                            headers=dict(problem=problem.internal_name,
                                         statements=str(invoker.get('statements', True)),
                                         binaries=str(invoker.get('binaries', True)))).text
        if res:
            problem.error = res
            break
    else:
        problem.error = ""
    problem.save()


@shared_task(queue='manager')
def delete_problem(problem_id):
    requests.post(settings.GIT_SERVICE_URL + '/DelProblem', headers=dict(problem=problem_id),
                  auth=('git', settings.GIT_SERVICE_PASSWORD))
    for invoker in settings.INVOKERS:
        requests.post(invoker['watchdog'] + '/DelProblem',
                      headers=dict(problem=problem_id))
