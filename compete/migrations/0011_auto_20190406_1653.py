# Generated by Django 2.2 on 2019-04-06 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compete', '0010_auto_20190406_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='contestregistration',
            name='score1',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='contestregistration',
            name='score2',
            field=models.IntegerField(default=0),
        ),
    ]
