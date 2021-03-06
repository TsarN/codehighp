# Generated by Django 2.2 on 2019-04-16 17:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('compete', '0021_auto_20190415_1726'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problem',
            name='coauthors',
        ),
        migrations.RemoveField(
            model_name='problem',
            name='owner',
        ),
        migrations.CreateModel(
            name='ProblemPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access', models.CharField(choices=[('OW', 'Owner'), ('WR', 'Write'), ('RD', 'Read')], default='OW', max_length=2)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compete.Problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('problem', 'user')},
            },
        ),
        migrations.AddField(
            model_name='problem',
            name='access',
            field=models.ManyToManyField(through='compete.ProblemPermission', to=settings.AUTH_USER_MODEL),
        ),
    ]
