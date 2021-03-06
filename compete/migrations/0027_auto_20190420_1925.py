# Generated by Django 2.2 on 2019-04-20 19:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('compete', '0026_auto_20190420_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproblemstatus',
            name='legit',
            field=models.CharField(choices=[('CS', 'Submitted during contest'), ('US', 'Submitted during upsolving'), ('VC', 'Virtual contest submission')], default='US', max_length=2),
        ),
        migrations.AlterUniqueTogether(
            name='userproblemstatus',
            unique_together={('problem', 'user', 'legit')},
        ),
    ]
