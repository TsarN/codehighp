# Generated by Django 2.2 on 2019-04-18 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_customuser_is_problemsetter'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='deviation',
            field=models.IntegerField(default=350),
        ),
        migrations.AddField(
            model_name='customuser',
            name='rating',
            field=models.IntegerField(default=1500),
        ),
        migrations.AddField(
            model_name='customuser',
            name='volatility',
            field=models.FloatField(default=0.06),
        ),
    ]