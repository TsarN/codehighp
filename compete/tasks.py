import os
import tempfile

from celery import shared_task
from django.conf import settings

from compete.invoke import invoke
from compete.compile import compile_native
from compete.models import Run
from util import get_tempfile_name


@shared_task
def invoke_run(run_id, prob_id, lang_id, src):
    try:
        run = Run.objects.get(pk=run_id)
    except Run.DoesNotExist:
        return

    if lang_id not in settings.COMPILERS:
        run.status = Run.COMPILATION_ERROR
        run.save()
        return

    lang_conf = settings.COMPILERS[lang_id]

    src_file = get_tempfile_name() + lang_conf['suffix']
    with open(src_file, 'w') as f:
        f.write(src)

    if lang_conf['flavor'] == 'native':
        run.status = Run.RUNNING
        run.save()

        exe_path, verdict, compile_log = compile_native(src_file, lang_conf)
        if verdict != Run.ACCEPTED:
            run.status = verdict
            run.write_log(dict(compile=compile_log))
            run.save()
            return

        stats = invoke(exe_path, prob_id)
        os.remove(exe_path)
        run.score = stats['score']
        run.cpu_used = stats['avg_cpu']
        run.memory_used = stats['avg_mem']
        run.status = Run.ACCEPTED
        run.write_log(stats['log'])
    else:
        run.status = Run.INTERNAL_ERROR

    run.save()


def do_invoke_run(run_id):
    try:
        run = Run.objects.get(pk=run_id)
    except Run.DoesNotExist:
        return None

    prob_id = run.problem.internal_name
    lang_id = run.lang
    with open(run.src_path, 'r') as f:
        src = f.read()

    run.status = Run.IN_QUEUE
    run.score = 0
    run.cpu_used = 0
    run.memory_used = 0
    run.save()

    invoke_run.delay(run_id, prob_id, lang_id, src)
