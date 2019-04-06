import os.path
import gzip

from django.db import models
from django.conf import settings
import yaml
import msgpack
from django.utils import timezone

from users.models import CustomUser


class Contest(models.Model):
    KINDS = (
        ('CT', 'Classical contest'),
        ('TR', 'Training contest')
    )

    STATUS = (
        ('NS', 'Not started'),
        ('RN', 'Running'),
        ('FN', 'Finished')
    )

    CLASSICAL = 'CT'
    TRAINING = 'TR'

    NOT_STARTED = 'NS'
    RUNNING = 'RN'
    FINISHED = 'FN'

    name = models.CharField(max_length=255)
    kind = models.CharField(max_length=2, choices=KINDS)
    start_date = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    authors = models.ManyToManyField(CustomUser, related_name='authored_contests')
    participants = models.ManyToManyField(CustomUser, through='ContestRegistration', related_name='participating')

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Contest id=%d name=%r>" % (self.id, self.name)

    def get_timings(self):
        now = timezone.now()
        if now < self.start_date:
            return Contest.NOT_STARTED, self.start_date - now
        if now < self.start_date + self.duration:
            return Contest.RUNNING, self.start_date + self.duration - now
        return Contest.FINISHED, None

    @property
    def registration_open(self):
        return self.status != Contest.FINISHED

    @property
    def status(self):
        return self.get_timings()[0]

    def timer(self):
        status, remaining = self.get_timings()
        status = dict(Contest.STATUS)[status]
        status = '<b>{}</b>'.format(status)
        if remaining:
            status += '<br /><span class="timer" data-timer="{}"></span>'\
                .format(round(remaining.total_seconds()))
        return status


class ContestRegistration(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    official = models.BooleanField(default=True)


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
    contest = models.ForeignKey(Contest, null=True, blank=True, default=None, on_delete=models.SET_NULL)

    def __str__(self):
        return "{}. {}".format(self.id, self.name)

    def __repr__(self):
        return "<Problem id=%d name=%r>" % (self.id, self.name)

    @property
    def config(self):
        if hasattr(self, "_config"):
            return self._config
        with open(os.path.join(settings.PROBLEM_DIR, self.internal_name, "problem.yaml")) as f:
            self._config = yaml.safe_load(f)
        return self._config

    @property
    def humanized_limits(self):
        result = "Flavor: <a href=\"/help/flavors/{0}\">{0}</a>\n".format(self.config.get('flavor'))
        for limit, msg, factor in self.LIMITS:
            value = self.config.get('limits', {}).get(limit)
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

    LEGIT = (
        ('CS', 'Submitted during contest'),
        ('US', 'Submitted during upsolving'),
        ('VC', 'Virtual contest submission')
    )

    UNKNOWN = 'UK'
    IN_QUEUE = 'IQ'
    RUNNING = 'RG'
    COMPILATION_ERROR = 'CE'
    ACCEPTED = 'AC'
    IGNORED = 'IG'
    INTERNAL_ERROR = 'IE'
    SECURITY_VIOLATION = 'SV'

    DURING_CONTEST = 'CS'
    DURING_UPSOLVING = 'US'
    VIRTUAL = 'VC'

    SCORE_DIVISOR = 1000

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    lang = models.CharField(max_length=16, choices=settings.COMPILERS_ENUM)
    status = models.CharField(max_length=2, choices=STATUS, default=UNKNOWN)
    cpu_used = models.PositiveIntegerField(help_text="in milliseconds", default=0)
    memory_used = models.PositiveIntegerField(help_text="in kilobytes", default=0)
    score = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    legit = models.CharField(max_length=2, choices=LEGIT, default=DURING_UPSOLVING)

    def __str__(self):
        return "Run #{}".format(self.id)

    def __repr__(self):
        return "<Run id=%d>" % self.id

    @property
    def src_path(self):
        suff = settings.COMPILERS[self.lang]['suffix']
        return os.path.join(settings.DATA_DIR, 'runs', '%06d%s' % (self.id, suff))

    @property
    def log_path(self):
        return os.path.join(settings.LOG_DIR, '%06d.gz' % self.id)

    @property
    def normalized_score(self):
        return self.score / 1000

    def accessible_by(self, user):
        if user.is_superuser:
            return True
        return self.user_id == user.id

    def write_log(self, log):
        log['status'] = self.status
        with gzip.open(self.log_path, 'wb') as f:
            msgpack.pack(log, f)

    def read_log(self):
        try:
            with gzip.open(self.log_path, 'rb') as f:
                return msgpack.unpack(f)
        except:
            return {}

    def delete_log(self):
        try:
            os.remove(self.log_path)
        except:
            pass