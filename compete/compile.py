import os
import subprocess

from django.conf import settings

from compete.models import Run
from util import get_tempfile_name


def compile_native(src, lang_conf):
    exe = get_tempfile_name()
    obj = os.path.join(settings.BASE_DIR, 'native', 'native', 'bin', lang_conf['obj'])
    compile_cmd = []
    for i in lang_conf['compile']:
        if i == '[src]':
            compile_cmd.append(src)
        elif i == '[exe]':
            compile_cmd.append(exe)
        elif i == '[obj]':
            compile_cmd.append(obj)
        else:
            compile_cmd.append(i)
    compile_cmd += ["-I", os.path.join(settings.BASE_DIR, 'native', 'include')]
    try:
        res = subprocess.run(compile_cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=10, universal_newlines=True)
    except subprocess.TimeoutExpired:
        return exe, Run.COMPILATION_ERROR, 'Took too long to compile'
    except:
        return exe, Run.COMPILATION_ERROR, 'Unknown error'

    if res.returncode != 0:
        return exe, Run.COMPILATION_ERROR, res.stdout

    return exe, Run.ACCEPTED, None


def compile_run(src, lang_conf, no_delete=False):
    if lang_conf.get('interpreted'):
        return src, Run.ACCEPTED, ''
    else:
        exe_path, verdict, compile_log = compile_native(src, lang_conf)
        if not no_delete:
            os.remove(src)
        return exe_path, verdict, compile_log
