import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_countries.fields import CountryField

from codehighp.redis import redis_conn


class CustomUser(AbstractUser):
    bio = models.CharField(max_length=200, help_text="A bit about yourself", blank=True, default='')
    country = CountryField(blank=True, null=True, default=None)
    is_problemsetter = models.BooleanField(blank=True, default=False)

    @property
    def html_link(self):
        css_class = "user-link"
        if self.is_superuser:
            css_class = "admin-link"
        return mark_safe('<a href="{}" class="{}">{}</a>'.format(
            reverse('profile', args=(self.username,)),
            css_class,
            self.username
        ))

    @property
    def is_online(self):
        return bool(redis_conn.get('user:%d:online' % self.id))

    @property
    def last_online(self):
        ts = redis_conn.get('user:%d:last_online' % self.id)
        if not ts:
            return None
        return datetime.datetime.fromtimestamp(int(ts))
