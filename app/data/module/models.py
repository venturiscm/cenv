from django.conf import settings
from django.db import models as django

from settings.roles import Roles
from data.state.models import State
from systems.models import environment, group, provider
from utility.runtime import Runtime

import os


class ModuleFacade(
    provider.ProviderModelFacadeMixin,
    group.GroupModelFacadeMixin,
    environment.EnvironmentModelFacadeMixin
):
    def get_packages(self):
        return super().get_packages() + ['module']

    def ensure(self, command, reinit = False):
        if reinit or command.get_state('module_ensure', True):
            if not self.retrieve(settings.CORE_MODULE):
                command.options.add('module_provider_name', 'sys_internal')
                command.module_provider.create(settings.CORE_MODULE, {})

            for module in command.get_instances(self):
                module.provider.load_parents()

            command.exec_local('module install', {
                'verbosity': command.verbosity
            })
            command.set_state('module_ensure', False)

    def keep(self):
        return settings.CORE_MODULE

    def get_relations(self):
        return {
            'groups': ('group', 'Groups', '--groups')
        }

    def get_list_fields(self):
        return (
            ('name', 'Name'),
            ('type', 'Type'),
            ('status', 'Status'),
            ('remote', 'Remote'),
            ('reference', 'Reference')
        )

    def get_display_fields(self):
        return (
            ('name', 'Name'),
            ('environment', 'Environment'),
            ('type', 'Type'),
            ('status', 'Status'),
            '---',
            ('config', 'Configuration'),
            '---',
            ('remote', 'Remote'),
            ('reference', 'Reference'),
            '---',
            ('created', 'Created'),
            ('updated', 'Updated')
        )

    def get_field_remote_display(self, instance, value, short):
        return value

    def get_field_reference_display(self, instance, value, short):
        return value

    def get_field_status_display(self, instance, value, short):
        path = instance.provider.module_path(instance.name, ensure = False)
        cenv_path = os.path.join(path, 'cenv.yml')

        if os.path.isfile(cenv_path):
            return self.success_color('valid')
        return self.error_color('invalid')


class Module(
    provider.ProviderMixin,
    group.GroupMixin,
    environment.EnvironmentModel
):
    remote = django.CharField(null=True, max_length=256)
    reference = django.CharField(null=True, max_length=128)

    class Meta(environment.EnvironmentModel.Meta):
        verbose_name = "module"
        verbose_name_plural = "modules"
        facade_class = ModuleFacade
        ordering = ['-type', 'name']
        provider_name = 'module'

    def allowed_groups(self):
        return [ Roles.admin, Roles.module_admin ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        State.facade.store('module_ensure', value = True)
        State.facade.store('group_ensure', value = True)
