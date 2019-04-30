"""
This files defines graders for problems.
Each grader is a function, which takes two arguments - a dict of variables
and a dict of parameters.
and returns tuple:
(normalized secondary score, cpu, mem)

Following variables are always available:
min_cpu, max_cpu, avg_cpu, limit_cpu,
min_mem, max_mem, avg_mem, limit_mem
"""


VALID_GRADERS = ["linear"]


def linear(vars, params):
    cpu_mode = params.get('cpu_mode')
    if cpu_mode not in ['min', 'max', 'avg']:
        cpu_mode = 'max'

    mem_mode = params.get('mem_mode')
    if mem_mode not in ['min', 'max', 'avg']:
        mem_mode = 'max'

    cpu_weight = params.get('cpu_weight')
    if (type(cpu_weight) not in [int, float]) or cpu_weight < 0:
        cpu_weight = .5

    mem_weight = params.get('mem_weight')
    if (type(mem_weight) not in [int, float]) or mem_weight < 0:
        mem_weight = .5

    cpu = cpu_weight * vars['{}_cpu'.format(cpu_mode)] / vars['limit_cpu']
    mem = mem_weight * vars['{}_mem'.format(mem_mode)] / vars['limit_mem']

    return 1 - (cpu + mem), vars['{}_cpu'.format(cpu_mode)], vars['{}_mem'.format(mem_mode)]
