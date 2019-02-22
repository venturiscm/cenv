# Generated by Django 2.1.3 on 2019-02-22 03:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import systems.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('network', '0013_networkpeer_type'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='networkpeer',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='networkpeer',
            name='environment',
        ),
        migrations.RemoveField(
            model_name='networkpeer',
            name='peers',
        ),
        migrations.AddField(
            model_name='firewall',
            name='created_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='firewall',
            name='updated_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='firewallrule',
            name='_cidrs',
        ),
        migrations.AddField(
            model_name='firewallrule',
            name='cidrs',
            field=systems.models.CSVField(null=True),
        ),
        migrations.AddField(
            model_name='firewallrule',
            name='created_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='firewallrule',
            name='updated_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='network',
            name='created_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='network',
            name='updated_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='subnet',
            name='created_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='subnet',
            name='updated_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='firewall',
            name='id',
            field=models.CharField(max_length=64, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='firewall',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='firewallrule',
            name='id',
            field=models.CharField(max_length=64, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='firewallrule',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='network',
            name='id',
            field=models.CharField(max_length=64, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='network',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='subnet',
            name='id',
            field=models.CharField(max_length=64, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='subnet',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterUniqueTogether(
            name='firewall',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='firewallrule',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='network',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='subnet',
            unique_together=set(),
        ),
        migrations.DeleteModel(
            name='NetworkPeer',
        ),
        migrations.RemoveField(
            model_name='firewall',
            name='_config',
        ),
        migrations.RemoveField(
            model_name='firewall',
            name='_state_config',
        ),
        migrations.RemoveField(
            model_name='firewall',
            name='_variables',
        ),
        migrations.RemoveField(
            model_name='firewall',
            name='network',
        ),
        migrations.RemoveField(
            model_name='firewall',
            name='type',
        ),
        migrations.RemoveField(
            model_name='firewallrule',
            name='_config',
        ),
        migrations.RemoveField(
            model_name='firewallrule',
            name='_state_config',
        ),
        migrations.RemoveField(
            model_name='firewallrule',
            name='_variables',
        ),
        migrations.RemoveField(
            model_name='firewallrule',
            name='firewall',
        ),
        migrations.RemoveField(
            model_name='firewallrule',
            name='type',
        ),
        migrations.RemoveField(
            model_name='network',
            name='_config',
        ),
        migrations.RemoveField(
            model_name='network',
            name='_state_config',
        ),
        migrations.RemoveField(
            model_name='network',
            name='_variables',
        ),
        migrations.RemoveField(
            model_name='network',
            name='environment',
        ),
        migrations.RemoveField(
            model_name='network',
            name='type',
        ),
        migrations.RemoveField(
            model_name='subnet',
            name='_config',
        ),
        migrations.RemoveField(
            model_name='subnet',
            name='_state_config',
        ),
        migrations.RemoveField(
            model_name='subnet',
            name='_variables',
        ),
        migrations.RemoveField(
            model_name='subnet',
            name='network',
        ),
        migrations.RemoveField(
            model_name='subnet',
            name='type',
        ),
    ]