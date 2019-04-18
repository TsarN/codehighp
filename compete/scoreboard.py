import attr
from django.db.transaction import atomic
from django.template.loader import render_to_string

from compete.models import UserProblemStatus, ContestRegistration, Problem


@attr.s
class ClassicScoreboardRow:
    me = attr.ib()
    place = attr.ib()
    user = attr.ib()
    score = attr.ib()
    score2 = attr.ib()
    problems = attr.ib()

    def render_to_html(self):
        return render_to_string('compete/scoreboard_row.html', dict(
            me=self.me,
            place=self.place,
            user=self.user,
            score=self.score,
            score2=self.score2,
            problems=self.problems
        ))


class ClassicScoreboard:
    def __init__(self, contest_id, user_id):
        self.rows = []
        self.problems = []
        self.contest_id = contest_id
        self.user_id = user_id

    def collect(self):
        with atomic():
            regs = list(ContestRegistration.objects
                        .filter(contest_id=self.contest_id, official=True, status=ContestRegistration.REGISTERED)
                        .order_by('-score', '-score2')
                        .select_related('user'))

            probs = list(Problem.objects.filter(contest_id=self.contest_id).order_by('short_name'))

            ps = list(UserProblemStatus.objects
                      .filter(problem_id__in=[x.id for x in probs],
                              user_id__in=[x.user_id for x in regs]))

        self.problems = probs
        prob_status = {}
        for x in ps:
            prob_status[x.user_id, x.problem_id] = x

        place = 0
        last_score = None
        places = {}

        for i, reg in enumerate(regs):
            if not last_score or (reg.score, reg.score2) < last_score:
                last_score = (reg.score, reg.score2)
                place = i
            places[i] = place

        for i, reg in enumerate(regs):
            self.rows.append(ClassicScoreboardRow(
                me=reg.user_id == self.user_id,
                place=places[i] + 1,
                user=reg.user,
                score=reg.score,
                score2=reg.score2,
                problems=[prob_status.get((reg.user_id, i.id)) for i in probs]
            ))

    def render_to_html(self):
        return render_to_string('compete/scoreboard_table.html', dict(
            problems=self.problems,
            rows=self.rows
        ))
