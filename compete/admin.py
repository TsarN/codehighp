from django.contrib import admin
from django.db import models

from compete.models import Problem, Run, Contest, ContestRegistration
from compete.tasks import do_invoke_run

admin.site.register(Problem)


def rejudge(modeladmin, request, queryset):
    for run in queryset:
        do_invoke_run(run)


def ignore(modeladmin, request, queryset):
    queryset.update(status=Run.IGNORED)


rejudge.short_description = "Rejudge selected runs"
ignore.short_description = "Ignore selected runs"


class RunAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'problem', 'status')
    list_filter = ('status',)
    actions = [rejudge, ignore]


admin.site.register(Run, RunAdmin)
admin.site.register(Contest)
admin.site.register(ContestRegistration)
