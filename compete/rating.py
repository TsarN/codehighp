# Glicko2 algorithm http://www.glicko.net/glicko/glicko2.pdf

import math

import attr
from django.db.transaction import atomic

from compete.models import ContestRegistration, RatingChange

TAU = 0.7
EPS = 0.000001
CONV = 173.7178


@attr.s
class Opponent:
    score = attr.ib()
    rating = attr.ib()
    deviation = attr.ib()


def g(phi):
    return 1 / math.sqrt(1 + 3 * (phi ** 2 / math.pi ** 2))


def elo(u, uj, phi):
    return 1 / (1 + math.exp(-g(phi) * (u - uj)))


def calculate_rating_change(r, rd, vol, opponents):
    if not opponents:
        return r, rd, vol

    mu = (r - 1500) / CONV
    phi = rd / CONV

    v = 0
    delta = 0
    for op in opponents:
        e = elo(mu, op.rating, op.deviation)
        v += (g(op.deviation) ** 2) * e * (1 - e)
        delta += g(op.deviation) * (op.score - e)
    v **= -1
    delta *= v

    a = math.log(vol ** 2)

    def f(x):
        return (math.exp(x) * (delta ** 2 - phi ** 2 - v - math.exp(x))) / \
               (2 * (phi ** 2 + v + math.exp(x)) ** 2) - (x - a) / (TAU ** 2)

    A = a
    if delta ** 2 > phi ** 2 + v:
        B = math.log(delta ** 2 - phi ** 2 - v)
    else:
        k = 1
        while f(a - k * TAU) < 0:
            k += 1
        B = a - k * TAU
    fa = f(A)
    fb = f(B)

    while math.fabs(B - A) > EPS:
        C = A + (A - B) * fa / (fb - fa)
        fc = f(C)
        if fc * fb < 0:
            A = B
            fa = fb
        else:
            fa /= 2
        B = C
        fb = fc

    volatility = math.exp(A / 2)
    ps = math.sqrt(phi ** 2 + volatility ** 2)
    deviation = 1 / math.sqrt(1 / (ps ** 2) + 1 / v)
    rating = 0
    for op in opponents:
        e = elo(mu, op.rating, op.deviation)
        rating += g(op.deviation) * (op.score - e)
    rating = mu + rating * (deviation ** 2)

    rating = CONV * rating + 1500
    deviation *= CONV

    rating = round(rating)
    deviation = round(deviation)

    return rating, deviation, volatility


def update_contest_rating(contest_id):
    regs = list(ContestRegistration.objects
                .filter(contest_id=contest_id, official=True, status=ContestRegistration.REGISTERED)
                .order_by('-score', '-score2')
                .select_related('user'))

    changes = []

    for reg in regs:
        opponents = []
        s = (reg.score, reg.score2)
        for op in regs:
            if reg.user_id == op.user_id:
                continue

            ops = (op.score, op.score2)
            if s > ops:
                score = 1
            elif s < ops:
                score = 0
            else:
                score = 0.5

            opponents.append(Opponent(
                score=score,
                rating=(op.user.rating - 1500) / CONV,
                deviation=op.user.deviation / CONV
            ))

        rating, deviation, volatility = calculate_rating_change(
            reg.user.rating, reg.user.deviation, reg.user.volatility, opponents)

        change = RatingChange(user=reg.user, contest_id=contest_id)

        change.old_rating = reg.user.rating
        change.old_deviation = reg.user.deviation
        change.old_volatility = reg.user.volatility
        change.new_rating = rating
        change.new_deviation = deviation
        change.new_volatility = volatility

        reg.user.rating = rating
        reg.user.deviation = deviation
        reg.user.volatility = volatility
        reg.user.is_rated = True

        changes.append(change)
        changes.append(reg.user)

    with atomic():
        for change in changes:
            change.save()
