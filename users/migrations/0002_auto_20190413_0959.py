# Generated by Django 2.2 on 2019-04-13 09:59

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='bio',
            field=models.CharField(blank=True, default='', help_text='A bit about yourself', max_length=200),
        ),
        migrations.AddField(
            model_name='customuser',
            name='country',
            field=django_countries.fields.CountryField(blank=True, default=None, max_length=2, null=True),
        ),
    ]
