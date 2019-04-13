import datetime

from django.conf import settings

from codehighp.redis import redis_conn


class TrackLastLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            redis_conn.setex('user:%d:online' % request.user.id, settings.ONLINE_TIMEOUT, 1)
            redis_conn.set('user:%d:last_online' % request.user.id, round(datetime.datetime.utcnow().timestamp()))

        response = self.get_response(request)
        return response
