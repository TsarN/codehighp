import hashlib
import os
import tempfile
import filecmp

import yaml
import json
import subprocess

from django.conf import settings

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


def gen_test(gen, input_path, params):
    with open(input_path, 'wb') as f:
        subprocess.run([gen], stdout=f, env={k: str(v) for k, v in params.items()})


def get_seed(s):
    h = hashlib.sha256()
    h.update(settings.SECRET_KEY.encode())
    h.update(s.encode())
    return int.from_bytes(h.digest()[:4], byteorder='little') % (2 ** 30)


def run_test(exe, gen, prob_id, prob_conf, group, n):
    solution = os.path.join(settings.PROBLEM_DIR, prob_id, 'bin', 'solve')
    runner = os.path.join(settings.BASE_DIR, 'native', prob_conf['flavor'], 'bin', 'runner')
    params = prob_conf['groups'][group]['vars'].copy()
    params['RAND_SEED'] = get_seed("{}_{}_{}".format(prob_id, group, n))

    real_time_limit = prob_conf['limits']['real_time'] // 1000
    cpu_time_limit = prob_conf['limits']['cpu_time']
    address_space_limit = prob_conf['limits']['address_space']

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, 'input')
        output_path = os.path.join(tmpdir, 'output')
        answer_path = os.path.join(tmpdir, 'answer')

        gen_test(gen, input_path, params)

        with open(input_path, 'rb') as input_file, open(answer_path, 'wb') as answer_file:
            subprocess.run([solution], stdin=input_file, stdout=answer_file)

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
    return dict(score=score, score2=score2, cpu=max_cpu, mem=max_mem, log=log)
