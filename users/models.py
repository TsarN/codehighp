import datetime

from django.conf import settings
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

    is_rated = models.BooleanField(default=False, blank=True)
    rating = models.IntegerField(default=1500)
    deviation = models.IntegerField(default=350)
    volatility = models.FloatField(default=0.06)

    @property
    def html_link(self):
        return self.get_html_link(self.username)

    @property
    def html_link_country(self):
        return self.get_html_link('<i class="{}" title="{}"></i> {}'.format(
            self.country.flag_css, self.country.name, self.username
        ))

    @property
    def rank(self):
        from compete.rating import get_rank
        if self.is_superuser:
            return "Administrator"
        if not self.is_rated:
            return "Unrated user"
        return get_rank(self.rating)[0]

    @property
    def color(self):
        from compete.rating import get_rank
        return get_rank(self.rating)[2]

    def get_html_link(self, title):
        from compete.rating import get_rank
        css_class = ""
        style = ""
        if self.is_superuser:
            css_class = " rated-user-link admin-link"
        elif self.is_rated:
            css_class = " rated-user-link"
            style = 'style="color: {}"'.format(get_rank(self.rating)[2])
        return mark_safe('<a href="{}" class="user-link{}" title="{} {}" {}>{}</a>'.format(
            reverse('profile', args=(self.username,)),
            css_class,
            self.rank,
            self.username,
            style,
            title
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
