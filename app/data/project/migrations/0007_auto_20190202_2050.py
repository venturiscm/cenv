# Generated by Django 2.1.3 on 2019-02-03 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_project__state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='_state',
        ),
        migrations.AddField(
            model_name='project',
            name='_state_config',
            field=models.TextField(db_column='state', null=True),
        ),
    ]
