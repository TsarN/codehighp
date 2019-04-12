# Generated by Django 2.2 on 2019-04-11 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compete', '0014_auto_20190411_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contestregistration',
            name='status',
            field=models.CharField(choices=[('OK', 'Registered'), ('PD', 'Pending'), ('RJ', 'Rejected')], db_index=True, default='OK', max_length=2),
        ),
    ]
