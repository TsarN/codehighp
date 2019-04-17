# Generated by Django 2.2 on 2019-04-15 17:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('compete', '0018_auto_20190413_2024'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='coauthors',
            field=models.TextField(default='', verbose_name=users.models.CustomUser),
        ),
        migrations.AddField(
            model_name='problem',
            name='owner',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='problem',
            name='unlisted',
            field=models.BooleanField(default=True),
        ),
    ]