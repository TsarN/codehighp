# Generated by Django 2.2 on 2019-04-12 13:19

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('compete', '0016_auto_20190411_1704'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='contestregistration',
            unique_together={('user', 'contest')},
        ),
    ]
