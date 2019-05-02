import base64
import os.path
import gzip
import struct

import markdown2
import requests
from django.core.exceptions import PermissionDenied
from django.db import models
from django.conf import settings
import yaml
import msgpack
from django.db.models import Sum, F, Q, Prefetch
from django.db.transaction import atomic
from django.utils import timezone

from users.models import CustomUser


class Contest(models.Model):
    KINDS = (
        ('CT', 'Classical contest'),
        ('TR', 'Training contest')
    )

    REGISTRATION = (
        ('OP', 'Open registration'),
        ('MD', 'Moderated registration'),
        ('IN', 'Only by invites'),
    )

    STATUS = (
        ('NS', 'Not started'),
        ('RN', 'Running'),
        ('FN', 'Finished')
    )

    CLASSICAL = 'CT'
    TRAINING = 'TR'

    OPEN_REGISTRATION = 'OP'
    MODERATED_REGISTRATION = 'MD'
    ONLY_BY_INVITES = 'IN'

    NOT_STARTED = 'NS'
    RUNNING = 'RN'
    FINISHED = 'FN'

    name = models.CharField(max_length=255)
    kind = models.CharField(max_length=2, choices=KINDS)
    registration = models.CharField(max_length=2, choices=REGISTRATION, default=OPEN_REGISTRATION)
    visible = models.BooleanField(blank=True, default=True, help_text="Is this contest visible to non-participants?")
    start_date = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    authors = models.ManyToManyField(CustomUser, related_name='authored_contests')
    participants = models.ManyToManyField(CustomUser, through='ContestRegistration', related_name='participating')
    is_rated = models.BooleanField(blank=True, default=True)
    rating_applied = models.BooleanField(blank=True, default=False)
    posts = models.ManyToManyField('blog.Post', related_name='contests', blank=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Contest id=%d name=%r>" % (self.id, self.name)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        from compete.tasks import update_contest_status
        super(Contest, self).save(force_insert=force_insert, force_update=force_update,
                                  using=using, update_fields=update_fields)

        update_contest_status(self.id)
        if self.start_date:
            update_contest_status.apply_async((self.id,), eta=self.start_date)
            if self.duration:
                update_contest_status.apply_async((self.id,), eta=self.start_date + self.duration)

    def can_access(self, user_id):
        if self.status == Contest.NOT_STARTED:
            return False
        if self.visible:
            return True
        return ContestRegistration.objects.filter(
            user_id=user_id, contest_id=self.id, status=ContestRegistration.REGISTERED).exists()

    def can_see(self, user_id):
        if user_id is None:
            return self.visible
        if ContestRegistration.objects.filter(user_id=user_id, contest_id=self.id).exists():
            return True
        return self.visible

    def can_register(self, user_id):
        if not self.registration_open or not self.visible:
            return False
        return not ContestRegistration.objects.filter(
            user_id=user_id, contest_id=self.id).exists()

    def ensure_can_access(self, user_id):
        if self.status == Contest.NOT_STARTED:
            raise PermissionDenied
        reg = list(ContestRegistration.objects.filter(user_id=user_id, contest_id=self.id))
        if self.visible:
            return reg[0] if reg else None
        if not reg or reg[0].status != ContestRegistration.REGISTERED:
            raise PermissionDenied
        return reg[0]

    @staticmethod
    def get_visible(qs, user_id):
        if not user_id:
            return qs.filter(visible=True)
        regs = {i.contest_id: i for i in ContestRegistration.objects.filter(user_id=user_id)}
        contests = []
        for contest in qs:
            if contest.visible or (contest.id in regs and regs[contest.id].status == ContestRegistration.REGISTERED):
                contests.append(contest)
        return contests

    def get_timings(self):
        now = timezone.now()
        if not self.start_date:
            return Contest.RUNNING, None
        if now < self.start_date:
            return Contest.NOT_STARTED, self.start_date - now
        if not self.duration:
            return Contest.RUNNING, None
        if now < self.start_date + self.duration:
            return Contest.RUNNING, self.start_date + self.duration - now
        return Contest.FINISHED, None

    @property
    def registration_open(self):
        return self.status == Contest.NOT_STARTED and self.registration != Contest.ONLY_BY_INVITES

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

    def card_timer(self):
        status, remaining = self.get_timings()
        status = dict(Contest.STATUS)[status]
        status = '<h3>{}</h3>'.format(status)
        if remaining:
            status += '<p class="timer" data-timer="{}"></p>'\
                .format(round(remaining.total_seconds()))
        return status


class ContestRegistration(models.Model):
    class Meta:
        unique_together = (('user', 'contest'),)

    STATUS = (
        ('OK', 'Registered'),
        ('PD', 'Registration pending'),
        ('RJ', 'Registration rejected')
    )

    REGISTERED = 'OK'
    PENDING = 'PD'
    REJECTED = 'RJ'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, default=REGISTERED, choices=STATUS, db_index=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    official = models.BooleanField(default=True)
    score = models.IntegerField(default=0)
    score2 = models.IntegerField(default=0)

    def __str__(self):
        return "Registration of user #%d for contest #%d" % (self.user_id, self.contest_id)


class Problem(models.Model):
    LIMITS_native = (
        ('real_time', 'Max time per test: %.1f sec', 10**-3),
        ('cpu_time', 'Max CPU time per test: %.1f sec', 10**-3),
        ('address_space', 'Max memory per test: %.1f MiB', 1/1024),
        ('source_size', 'Max source code size: %.1f KiB', 1 / 1024),
        ('threads', 'Max threads allowed: %d', 1),
    )

    LIMITS_vm = (
        ('cpu_time', 'Max execution time per test: %d cycles', 1),
        ('address_space', 'Max memory per test: %d cells', 1),
        ('source_size', 'Max source code size: %.1f KiB', 1 / 1024),
    )

    VISIBILITY = (
        ('AA', 'Make visible for everyone when contest starts'),
        ('AR', 'Make visible for contest participants when contest starts'),
        ('VA', 'Visible for everyone'),
        ('VR', 'Visible for contest participants'),
        ('IN', 'Invisible'),
    )

    AUTO_VISIBLE_EVERYONE = 'AA'
    AUTO_VISIBLE_PARTICIPANTS = 'AR'
    VISIBLE_EVERYONE = 'VA'
    VISIBLE_PARTICIPANTS = 'VR'
    INVISIBLE = 'IN'

    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=16, default='', blank=True)
    internal_name = models.CharField(max_length=255)
    contest = models.ForeignKey(Contest, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    score = models.IntegerField(default=0)
    visibility = models.CharField(max_length=2, choices=VISIBILITY, default=AUTO_VISIBLE_EVERYONE)
    access = models.ManyToManyField(CustomUser, through='ProblemPermission')
    unlisted = models.BooleanField(blank=False, default=True)
    error = models.TextField(default='', blank=True)

    def __str__(self):
        return "{}. {}".format(self.id, self.name)

    def __repr__(self):
        return "<Problem id=%d name=%r>" % (self.id, self.name)

    def get_access(self, user_id):
        perm = list(ProblemPermission.objects.filter(problem_id=self.id, user_id=user_id))
        if not perm:
            return None
        return perm[0].access

    def update_git_permissions(self):
        perms = ProblemPermission.objects\
            .filter(problem_id=self.id)\
            .select_related('user')
        data = []
        for perm in perms:
            access = 'R' if perm.access == ProblemPermission.READ else 'RW+'
            data.append(dict(access=access, user=perm.user.username))
        res = requests.post(settings.GIT_SERVICE_URL + '/SetPermissions',
                      headers=dict(problem=self.internal_name),
                      json=data, auth=('git', settings.GIT_SERVICE_PASSWORD))
        print(res, res.text)

    @property
    def repo_url(self):
        return '{}:/problems/{}.git'.format(settings.GIT_REPO_URL, self.internal_name)

    def is_visible(self, user_id):
        if self.error:
            return False
        if ProblemPermission.objects.filter(problem_id=self.id, user_id=user_id).exists():
            return True
        if self.unlisted:
            return False
        if self.visibility in [Problem.AUTO_VISIBLE_EVERYONE, Problem.AUTO_VISIBLE_PARTICIPANTS, Problem.INVISIBLE]:
            return False
        if self.visibility in [Problem.VISIBLE_EVERYONE]:
            return True

        return ContestRegistration.objects.filter(contest_id=self.contest_id,
                                                  user_id=user_id,
                                                  status=ContestRegistration.REGISTERED).exists()

    @property
    def full_name(self):
        if self.contest_id:
            return "{}. {}".format(self.short_name, self.name)
        else:
            return "{}. {}".format(self.pk, self.name)

    @property
    def config(self):
        if hasattr(self, "_config"):
            return self._config
        with open(os.path.join(settings.PROBLEM_DIR, self.internal_name, "problem.yaml")) as f:
            self._config = yaml.safe_load(f)
        return self._config

    def get_samples(self):
        def expand(fmt, data):
            actdata = [i for i in data if i != '\\n']
            human = ' '.join(map(str, data))
            human = '\n'.join(i.strip() for i in human.split('\\n'))
            encoded = base64.b64encode(struct.pack(fmt, *actdata)).decode()

            return dict(human=human, encoded=encoded)

        res = []
        for sample in self.config.get('samples', []):
            inp = expand(sample['input']['format'], sample['input']['data'])
            ans = expand(sample['answer']['format'], sample['answer']['data'])

            instr = '''
<p>Assuming your solution is named <code>./a.out</code>, running the following in your shell:</p>
<pre>echo '{}' | base64 -d | ./a.out | base64</pre> <p>should produce</p>
<pre>{}</pre>
'''.format(inp['encoded'], ans['encoded'])

            res.append(dict(inp=inp['human'], ans=ans['human'], instr=instr))

        return res

    @property
    def statement(self):
        if hasattr(self, "_statement"):
            return self._statement
        with open(os.path.join(settings.PROBLEM_DIR, self.internal_name, 'bin', 'statement.html')) as f:
            self._statement = f.read()
        return self._statement

    @property
    def humanized_limits(self):
        result = "Flavor: <a href=\"/help/flavors/{0}\">{0}</a>\n".format(self.config.get('flavor'))
        for limit, msg, factor in getattr(self, 'LIMITS_{}'.format(self.config['flavor'].split('.')[0])):
            value = self.config.get('limits', {}).get(limit)
            if not value:
                continue
            value *= factor
            result += msg % value + "\n"
        return result


class ProblemPermission(models.Model):
    class Meta:
        unique_together = (('problem', 'user'),)

    ACCESS = (
        ('OW', 'Owner'),
        ('WR', 'Write'),
        ('RD', 'Read'),
    )

    OWNER = 'OW'
    WRITE = 'WR'
    READ = 'RD'

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    access = models.CharField(max_length=2, choices=ACCESS, default=OWNER)


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
    date = models.DateTimeField(auto_now_add=True, blank=True)
    score = models.IntegerField(default=0)
    score2 = models.IntegerField(default=0)
    legit = models.CharField(max_length=2, choices=LEGIT, default=DURING_UPSOLVING)

    def __str__(self):
        return "Run #{}".format(self.id)

    def __repr__(self):
        return "<Run id=%d>" % self.id

    @property
    def friendly_status(self):
        if self.status != Run.ACCEPTED:
            return self.get_status_display()
        if self.score >= Run.SCORE_DIVISOR:
            return "<b>Full solution</b>"
        else:
            return "Partial solution"

    @atomic
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        status, created = UserProblemStatus.objects.get_or_create(
            problem_id=self.problem_id,
            user_id=self.user_id,
            legit=self.legit or Run.DURING_UPSOLVING
        )
        if created or (status.score, status.score2) < (self.score, self.score2):
            status.score = self.score
            status.score2 = self.score2
            status.save()
        super(Run, self).save(force_insert, force_update, using, update_fields)

    @property
    def src_path(self):
        suff = settings.COMPILERS[self.lang]['suffix']
        return os.path.join(settings.DATA_DIR, 'runs', '%06d%s' % (self.id, suff))

    @property
    def log_path(self):
        return os.path.join(settings.LOG_DIR, '%06d.gz' % self.id)

    @property
    def html_score(self):
        score = self.score / Run.SCORE_DIVISOR
        score2 = self.score2 / Run.SCORE_DIVISOR
        return "%.3f <small>/ %.3f</small>" % (score, score2)

    def accessible_by(self, user):
        if user.is_superuser:
            return True
        return self.user_id == user.id

    def write_log(self, log):
        log['status'] = self.status
        if settings.MAIN_WATCHDOG:
            data = msgpack.packb(log)
            requests.post(settings.MAIN_WATCHDOG + '/UploadLog', data=data, headers=dict(run=str(self.id)))
        else:
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


class UserProblemStatus(models.Model):
    class Meta:
        unique_together = (('problem', 'user', 'legit'),)

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    legit = models.CharField(max_length=2, choices=Run.LEGIT, default=Run.DURING_UPSOLVING)
    score = models.IntegerField(default=0)
    score2 = models.IntegerField(default=0)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(UserProblemStatus, self).save(force_insert, force_update, using, update_fields)
        if not self.problem.contest_id or self.legit != Run.DURING_CONTEST:
            return

        with atomic():
            reg = ContestRegistration.objects.filter(user_id=self.user_id, contest_id=self.problem.contest_id,
                                                     status=ContestRegistration.REGISTERED)
            if not reg.exists():
                return

            reg = reg[0]

            res = UserProblemStatus.objects\
                .filter(user_id=self.user_id,
                        problem__contest_id=self.problem.contest_id,
                        legit=Run.DURING_CONTEST)\
                .aggregate(score=Sum(F('score')*F('problem__score')),
                           score2=Sum(F('score2')*F('problem__score')))
            score = round(res['score'] / Run.SCORE_DIVISOR)
            score2 = round(res['score2'] / Run.SCORE_DIVISOR)

            if (score, score2) > (reg.score, reg.score2):
                reg.score = score
                reg.score2 = score2
                reg.save()


class RatingChange(models.Model):
    class Meta:
        unique_together = (('user', 'contest'),)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)

    old_rating = models.IntegerField(default=0)
    old_deviation = models.IntegerField(default=0)
    old_volatility = models.FloatField(default=0)

    new_rating = models.IntegerField(default=0)
    new_deviation = models.IntegerField(default=0)
    new_volatility = models.FloatField(default=0)
