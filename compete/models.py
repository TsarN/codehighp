import os.path
import gzip

from django.db import models
from django.conf import settings
import yaml
import msgpack

from users.models import CustomUser


class Problem(models.Model):
    LIMITS = (
        ('real_time', 'Max time per test: %.1f sec', 10**-3),
        ('cpu_time', 'Max CPU time per test: %.1f sec', 10**-3),
        ('address_space', 'Max memory per test: %.1f MiB', 1/1024),
        ('source_size', 'Max source code size: %.1f KiB', 1 / 1024),
        ('threads', 'Max threads allowed: %d', 1),
    )

    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=16)
    internal_name = models.CharField(max_length=255)
    statement = models.TextField()

    def __str__(self):
        return "{}. {}".format(self.id, self.name)

    def __repr__(self):
        return "<Problem id=%d name=%s>" % (self.id, self.name)

    @property
    def limits(self):
        if hasattr(self, "_config"):
            return self._config.get('limits', dict())
        with open(os.path.join(settings.PROBLEM_DIR, self.internal_name, "problem.yaml")) as f:
            self._config = yaml.safe_load(f)
        return self._config.get('limits', dict())

    @property
    def humanized_limits(self):
        result = ""
        for limit, msg, factor in self.LIMITS:
            value = self.limits.get(limit)
            if not value:
                continue
            value *= factor
            result += msg % value + "\n"
        return result


class Run(models.Model):
    STATUS = (
        ('UK', 'Unknown'),
        ('IQ', 'In queue'),
        ('RG', 'Running'),
        ('CE', 'Compilation error'),
        ('AC', 'Accepted'),
        ('IG', 'Ignored'),
        ('IE', 'Internal error'),
        ('SV', 'Security violation')
    )

    UNKNOWN = 'UK'
    IN_QUEUE = 'IQ'
    RUNNING = 'RG'
    COMPILATION_ERROR = 'CE'
    ACCEPTED = 'AC'
    IGNORED = 'IG'
    INTERNAL_ERROR = 'IE'
    SECURITY_VIOLATION = 'SV'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    lang = models.CharField(max_length=16, choices=settings.COMPILERS_ENUM)
    status = models.CharField(max_length=2, choices=STATUS, default=UNKNOWN)
    cpu_used = models.PositiveIntegerField(help_text="in milliseconds")
    memory_used = models.PositiveIntegerField(help_text="in kilobytes")
    score = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return "Run #{}".format(self.id)

    def __repr__(self):
        return "<Run id=%d>" % self.id

    @property
    def src_path(self):
        suff = settings.COMPILERS[self.lang]['suffix']
        return os.path.join(settings.DATA_DIR, 'runs', '%06d%s' % (self.id, suff))

    def write_log(self, log):
        log['status'] = self.status
        path = os.path.join(settings.LOG_DIR, '%06d.gz' % self.id)
        with gzip.open(path, 'wb') as f:
            msgpack.pack(log, f)
