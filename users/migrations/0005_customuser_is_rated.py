# Generated by Django 2.2 on 2019-04-18 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20190418_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_rated',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
