from django.core.management import BaseCommand
from django.db.transaction import atomic

from compete.models import Problem
from problemsetting.tasks import update_problem_from_git


class Command(BaseCommand):
    help = 'Updates and rebuilds EVERY SINGLE PROBLEM from git'

    def handle(self, *args, **options):
        with atomic():
            for problem in Problem.objects.all():
                update_problem_from_git.delay(problem.id)
        print('Problems are now being updated asynchronously')
