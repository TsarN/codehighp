# Generated by Django 2.1.7 on 2019-03-31 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compete', '0003_run'),
    ]

    operations = [
        migrations.AddField(
            model_name='run',
            name='score',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='run',
            name='status',
            field=models.CharField(choices=[('UK', 'Unknown'), ('IQ', 'In queue'), ('RG', 'Running'), ('CE', 'Compilation error'), ('AC', 'Accepted'), ('IG', 'Ignored'), ('IE', 'Internal error'), ('SV', 'Security violation')], default='UK', max_length=2),
        ),
    ]