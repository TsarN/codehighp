import os
import base64

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

    src = base64.b64decode(src)

    if lang_id not in settings.COMPILERS:
        run.status = Run.COMPILATION_ERROR
        run.save()
        return

    lang_conf = settings.COMPILERS[lang_id]

    src_file = get_tempfile_name() + lang_conf['suffix']
    with open(src_file, 'wb') as f:
        f.write(src)

    if lang_conf['flavor'] == 'native':
        run.status = Run.RUNNING
        run.save()

        exe_path, verdict, compile_log = compile_native(src_file, lang_conf)
        os.remove(src_file)
        if verdict != Run.ACCEPTED:
            run.status = verdict
            run.write_log(dict(compile=compile_log))
            run.save()
            return

        stats = invoke(exe_path, prob_id)
        os.remove(exe_path)
        run.score = stats['score']
        run.cpu_used = stats['cpu']
        run.memory_used = stats['mem']
        run.status = Run.ACCEPTED
        run.write_log(stats['log'])
    else:
        run.status = Run.INTERNAL_ERROR

    run.save()


def do_invoke_run(run):
    prob_id = run.problem.internal_name
    lang_id = run.lang
    with open(run.src_path, 'rb') as f:
        src = f.read()
    src = base64.b64encode(src).decode()

    run.status = Run.IN_QUEUE
    run.score = 0
    run.cpu_used = 0
    run.memory_used = 0
    run.save()
    run.delete_log()

    invoke_run.delay(run.pk, prob_id, lang_id, src)
