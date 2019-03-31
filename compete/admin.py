from django.contrib import admin
from django.db import models

from compete.models import Problem, Run

admin.site.register(Problem)
admin.site.register(Run)