import hashlib
import os
import re
import shutil
import struct
import tempfile
import filecmp

import markdown2
import requests
import yaml
import json
import subprocess

from django.conf import settings

from compete.compile import compile_run
from compete.models import Run

VERDICTS = {
    'OK': 'OK',
    'RE': 'Runtime error',
    'SV': 'Security violation',
    'ML': 'Memory limit exceeded',
    'TL': 'Time limit exceeded',
    'RL': 'Real time limit exceeded',
    'IE': 'Internal error',
    'WA': 'Wrong answer',
}


def check_problem_configuration(problem_root):
    try:
        with open(os.path.join(problem_root, 'problem.yaml')) as f:
            conf = yaml.safe_load(f)
    except OSError as e:
        return "Couldn't open `problem.yaml`: " + e.strerror
    except yaml.YAMLError as e:
        return "Failed to parse `problem.yaml`: " + str(e)

    if conf.get('flavor') not in ['native', 'vm.brainfuck']:
        return "Invalid flavor"

    if conf.get('check') not in ['exact']:
        return "Invalid checker"

    limits = conf.get('limits')
    if type(limits) != dict:
        return "`limits` must be a dict"

    real_time = limits.get('real_time', 5000)
    if type(real_time) != int or real_time not in range(10001):
        return "`limits.real_time` must be an int in range [0, 10000]"

    cpu_time = limits.get('cpu_time', 1000)
    if type(cpu_time) != int or cpu_time <= 0:
        return "`limits.cpu_time` must be a positive int"

    address_space = limits.get('address_space', 262144)
    if type(address_space) != int or address_space not in range(2**20+1):
        return "`limits.address_space` must be an int in range [0, 1048576]"

    statement = conf.get('statement')
    if type(statement) != str or '/' in statement or not os.path.isfile(os.path.join(problem_root, statement)):
        return "Invalid statement"

    gen = conf.get('gen')
    if gen:
        if type(gen) != str or '/' in gen or not os.path.isfile(os.path.join(problem_root, gen)):
            return "Invalid generator"
        gen_lang = conf.get('gen_lang')
        if gen_lang not in settings.COMPILERS:
            return "Invalid generator lang"
        if settings.COMPILERS[gen_lang]['flavor'] != 'native':
            return "Generator must be native"

    solve = conf.get('solve')
    if type(solve) != str or '/' in solve or not os.path.isfile(os.path.join(problem_root, solve)):
        return "Invalid solver"

    solve_lang = conf.get('solve_lang')
    if solve_lang not in settings.COMPILERS or settings.COMPILERS[solve_lang]['flavor'] != conf.get('flavor'):
        return "Invalid solver lang"

    samples = conf.get('samples', [])
    if type(samples) != list:
        return "`samples` must be a list"

    for sample in samples:
        for k in ["input", "answer"]:
            x = sample.get(k)
            if type(x) != dict:
                return "`samples[??].{}` must be a dict".format(k)
            fmt = x.get('format')
            dat = x.get('data')

            if type(fmt) != str:
                return "`samples[??].{}.format` must be a string".format(k)
            if type(dat) != list:
                return "`samples[??].{}.data` must be a list".format(k)

            dat = [i for i in dat if i != '\\n']

            try:
                packed = struct.pack(fmt, *dat)
            except:
                return "struct.pack failed, invalid format or data in sample"

    groups = conf.get('groups')
    if type(groups) != dict:
        return "`groups` must be a dict"

    i = 0
    while i in groups:
        i += 1

    if i > 100:
        return "no more than 100 test groups allowed"

    score = 0

    for k, v in groups.items():
        if k not in range(i):
            return "`groups` must be a dict with consecutive integer keys"
        s = v.get('score')
        if type(s) != int or s < 0:
            return "`groups[??].score` must be a non-negative int"
        score += s

        t = v.get('tests')
        if type(s) != int or t not in range(1, 101):
            return "`groups[??].tests` must be an int in range [1, 100]"

        if type(v.get('vars', {})) != dict:
            return "`groups[??].vars` must be a dict"

        for j in v.get('vars', {}).values():
            try:
                str(j)
            except:
                return "`groups[??].vars` values must be convertible to strings"

        if 'input_file' in v:
            if type(v['input_file']) != str:
                return "`groups[??].input_file` must be a string"
            try:
                for j in range(t):
                    fname = os.path.join(problem_root, v['input_file'] % j)
                    if not os.path.realpath(fname).startswith(problem_root):
                        return "input file escapes problem root"
                    if not os.path.isfile(fname):
                        return "input file {} not found".format(fname)
            except:
                return "input_file formatting error"
        else:
            if not gen:
                return "No generator or input_file"

    if score != Run.SCORE_DIVISOR:
        return "Group scores must add up to {}".format(Run.SCORE_DIVISOR)


def build_problem(prob_id, statements=True, binaries=True):
    problem_root = os.path.join(settings.PROBLEM_DIR, prob_id)
    err = check_problem_configuration(problem_root)
    if err:
        return "Configuration check failed: " + err
    with open(os.path.join(problem_root, 'problem.yaml')) as f:
        conf = yaml.safe_load(f)

    bin_root = os.path.join(problem_root, 'bin')

    if os.path.exists(bin_root):
        shutil.rmtree(bin_root)
    os.makedirs(bin_root)

    if statements:
        with open(os.path.join(problem_root, conf['statement'])) as f:
            html_statement = markdown2.markdown(f.read(), safe_mode=True)
            for group in set(re.findall(r'\$\$(.*?)\$\$', html_statement)):
                data = requests.post(settings.MATHOID_URL, data=dict(q=group, type='tex')).json()
                if not data['success']:
                    html_statement = html_statement.replace('$${}$$'.format(group),
                                                            'TeX error: {}'.format(data.get('log')))
                else:
                    html_statement = html_statement.replace('$${}$$'.format(group), data.get('svg'))

            for group in set(re.findall(r'\$(.*?)\$', html_statement)):
                data = requests.post(settings.MATHOID_URL, data=dict(q=group, type='inline-tex')).json()
                if not data['success']:
                    html_statement = html_statement.replace('${}$'.format(group),
                                                            'TeX error: {}'.format(data.get('log')))
                else:
                    html_statement = html_statement.replace('${}$'.format(group), data.get('svg'))

        with open(os.path.join(bin_root, 'statement.html'), 'w') as f:
            f.write(html_statement)

    if binaries:
        solve_src = os.path.join(problem_root, conf['solve'])
        solve_exe, verdict, log = compile_run(solve_src, settings.COMPILERS[conf['solve_lang']], no_delete=True)
        if verdict != Run.ACCEPTED:
            return log

        shutil.copy2(solve_exe, os.path.join(bin_root, 'solve'))
        if solve_exe != solve_src:
            os.remove(solve_exe)

        if 'gen' not in conf:
            return

        gen_src = os.path.join(problem_root, conf['gen'])

        gen_exe, verdict, log = compile_run(gen_src, settings.COMPILERS[conf['gen_lang']], no_delete=True)
        if verdict != Run.ACCEPTED:
            return log

        shutil.copy2(gen_exe, os.path.join(bin_root, 'gen'))
        if gen_exe != gen_src:
            os.remove(gen_exe)


def gen_test(gen, input_path, params):
    runner = os.path.join(settings.BASE_DIR, 'native', 'native', 'bin', 'runner')
    with open(input_path, 'wb') as f:
        subprocess.run([runner, gen, "10", "10000", "262144"],
                       stdin=subprocess.DEVNULL, stdout=f,
                       stderr=subprocess.DEVNULL, env=params)


def get_seed(s):
    h = hashlib.sha256()
    h.update(settings.SECRET_KEY.encode())
    h.update(s.encode())
    return str(int.from_bytes(h.digest()[:4], byteorder='little') % (2 ** 30))


def run_test(exe, gen, prob_id, prob_conf, group, n):
    solution = os.path.join(settings.PROBLEM_DIR, prob_id, 'bin', 'solve')
    runner = os.path.join(settings.BASE_DIR, 'native', prob_conf['flavor'], 'bin', 'runner')
    params = dict()
    if 'vars' in prob_conf['groups'][group]:
        for k, v in prob_conf['groups'][group]['vars'].items():
            params['CODEHIGHP_VAR_{}'.format(k)] = str(v)
    params['RAND_SEED'] = get_seed("{}_{}_{}".format(prob_id, group, n))

    real_time_limit = (prob_conf['limits'].get('real_time', 0) + 999) // 1000
    cpu_time_limit = prob_conf['limits']['cpu_time']
    address_space_limit = prob_conf['limits']['address_space']

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, 'output')
        answer_path = os.path.join(tmpdir, 'answer')

        if prob_conf['groups'][group].get('input_file'):
            input_path = os.path.join(settings.PROBLEM_DIR, prob_id, prob_conf['groups'][group]['input_file'] % n)
        else:
            input_path = os.path.join(tmpdir, 'input')
            gen_test(gen, input_path, params)

        with open(input_path, 'rb') as input_file, open(answer_path, 'wb') as answer_file:
            subprocess.run([runner, solution, str(real_time_limit),
                            str(cpu_time_limit), str(address_space_limit)],
                           stdin=input_file, stdout=answer_file, stderr=subprocess.DEVNULL)

        with open(input_path, 'rb') as input_file, open(output_path, 'wb') as output_file:
            res = subprocess.run([runner, exe, str(real_time_limit),
                                  str(cpu_time_limit), str(address_space_limit)],
                                 stdin=input_file, stdout=output_file, stderr=subprocess.PIPE)
            report = json.loads(res.stderr.decode())

        if os.path.getsize(input_path) < settings.MAX_LOG_FILE_SIZE:
            with open(input_path, 'rb') as f:
                report['input'] = f.read()

        if os.path.getsize(output_path) < settings.MAX_LOG_FILE_SIZE:
            with open(output_path, 'rb') as f:
                report['output'] = f.read()

        if os.path.getsize(answer_path) < settings.MAX_LOG_FILE_SIZE:
            with open(answer_path, 'rb') as f:
                report['answer'] = f.read()

        if report['verdict'] == 'OK' and report['exitcode'] != 0:
            report['verdict'] = 'RE'

        if report['verdict'] != 'OK':
            return False, report

        if prob_conf['check'] == 'exact':
            ok = filecmp.cmp(output_path, answer_path)
            if not ok:
                report['verdict'] = 'WA'
            return ok, report


def invoke(exe, prob_id):
    with open(os.path.join(settings.PROBLEM_DIR, prob_id, "problem.yaml")) as f:
        prob_conf = yaml.safe_load(f)
    gen = os.path.join(settings.PROBLEM_DIR, prob_id, 'bin', 'gen')

    score = 0
    max_cpu = 0
    max_mem = 0

    log = dict()

    for group in prob_conf['groups']:
        log[group] = dict(score=0)

    group = 0

    while group in prob_conf['groups']:
        ok, report = run_test(exe, gen, prob_id, prob_conf, group, 0)
        log[group][0] = report
        if ok:
            score += prob_conf['groups'][group]['score']
            log[group]['score'] += prob_conf['groups'][group]['score']
            group += 1
            continue
        else:
            break
    group -= 1

    while group >= 0:
        good = True
        max_cpu = log[group][0]['cpu']
        max_mem = log[group][0]['mem']
        tests = prob_conf['groups'][group]['tests']

        for n in range(1, tests):
            ok, report = run_test(exe, gen, prob_id, prob_conf, group, n)
            log[group][n] = report
            if not ok:
                good = False
                break
            max_cpu = max(max_cpu, report['cpu'])
            max_mem = max(max_mem, report['mem'])

        if not good:
            score -= prob_conf['groups'][group]['score']
            log[group]['score'] -= prob_conf['groups'][group]['score']
            group -= 1
        else:
            break

    score2 = max_cpu / prob_conf['limits']['cpu_time'] + max_mem / prob_conf['limits']['address_space']
    score2 /= 2
    score2 = 1 - score2
    if score == 0:
        score2 = 0
    return dict(score=score, score2=score2, cpu=max_cpu, mem=max_mem, log=log)
