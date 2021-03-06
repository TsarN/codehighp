# Generated by Django 2.1.7 on 2019-04-01 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compete', '0004_auto_20190331_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='run',
            name='cpu_used',
            field=models.PositiveIntegerField(default=0, help_text='in milliseconds'),
        ),
        migrations.AlterField(
            model_name='run',
            name='memory_used',
            field=models.PositiveIntegerField(default=0, help_text='in kilobytes'),
        ),
    ]
