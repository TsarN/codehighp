import os
import tempfile
import filecmp

import yaml
import json
import subprocess

from django.conf import settings


def gen_test(gen, input_path, params):
    with open(input_path, 'wb') as f:
        subprocess.run([gen], stdout=f, env={k: str(v) for k, v in params.items()})


def run_test(exe, gen, prob_id, prob_conf, group, n):
    solution = os.path.join(settings.PROBLEM_DIR, prob_id, 'bin', 'solve')
    runner = os.path.join(settings.DATA_DIR, prob_conf['flavor'], 'bin', 'runner')
    params = prob_conf['groups'][group]['vars'].copy()
    params['RAND_SEED'] = hash("{}_{}_{}".format(prob_id, group, n)) % (2 ** 30)

    real_time_limit = prob_conf['limits']['real_time'] // 1000
    cpu_time_limit = prob_conf['limits']['cpu_time']
    address_space_limit = prob_conf['limits']['address_space']

    with tempfile.TemporaryDirectory() as dir:
        input_path = os.path.join(dir, 'input')
        output_path = os.path.join(dir, 'output')
        answer_path = os.path.join(dir, 'answer')

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

        if report['verdict'] != 'OK' or report['exitcode'] != 0:
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
    group = 0

    score = 0
    avg_cpu = 0
    avg_mem = 0

    log = dict()

    while group in prob_conf['groups']:
        ok, report = run_test(exe, gen, prob_id, prob_conf, group, 0)
        log[group] = dict()
        log[group][0] = report
        if ok:
            score += prob_conf['groups'][group]['score']
            group += 1
            continue
        else:
            break
    group -= 1

    while group >= 0:
        good = True
        total_cpu = 0
        total_mem = 0
        tests = prob_conf['groups'][group]['tests']

        for n in range(tests):
            ok, report = run_test(exe, gen, prob_id, prob_conf, group, n)
            log[group][n] = report
            if not ok:
                good = False
                break
            total_cpu += report['cpu']
            total_mem += report['mem']

        if not good:
            score -= prob_conf['groups'][group]['score']
            group -= 1
            continue

        avg_cpu = round(total_cpu / tests)
        avg_mem = round(total_mem / tests)
        break

    return dict(score=score, avg_cpu=avg_cpu, avg_mem=avg_mem, log=log)
