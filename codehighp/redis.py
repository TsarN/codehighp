import redis
from django.conf import settings

redis_conn = redis.Redis(**settings.REDIS)
