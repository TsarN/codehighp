from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe


class CustomUser(AbstractUser):
    @property
    def html_link(self):
        return mark_safe('<a href="{}" class="user-link">{}</a>'.format(
            reverse('profile', args=(self.username,)),
            self.username
        ))
