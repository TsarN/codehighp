from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe


class CustomUser(AbstractUser):
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
