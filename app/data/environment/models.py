from django.conf import settings
from django.db import models as django

from systems.models import fields, base, resource, provider
from utility.runtime import Runtime


class EnvironmentFacade(
    provider.ProviderModelFacadeMixin,
    resource.ResourceModelFacadeMixin
):
    def get_packages(self):
        return [] # Do not export with db dumps!!

    def ensure(self, command):
        env_name = self.get_env()
        curr_env = self.retrieve(env_name)

        if not curr_env:
            curr_env = command.environment_provider.create(env_name, {})

        if not Runtime.data:
            curr_env.runtime_image = None
            curr_env.save()

    def keep(self):
        return self.get_env()


    def get_env(self):
        return Runtime.get_env()

    def set_env(self, name = None, repo = None, image = None):
        Runtime.set_env(name, repo, image)

    def delete_env(self):
        Runtime.delete_env()


    def get_field_host_display(self, instance, value, short):
        return value

    def get_field_port_display(self, instance, value, short):
        return value

    def get_field_user_display(self, instance, value, short):
        return value

    def get_field_token_display(self, instance, value, short):
        if short:
            return self.encrypted_color(value[:10] + '...')
        else:
            return self.encrypted_color(value)

    def get_field_repo_display(self, instance, value, short):
        return value

    def get_field_image_display(self, instance, value, short):
        return value

    def get_field_is_active_display(self, instance, value, short):
        return self.dynamic_color(str(value))


class Environment(
    provider.ProviderMixin,
    resource.ResourceModel
):
    host = django.URLField(null = True)
    port = django.IntegerField(default = 5123)
    user = django.CharField(max_length = 150, default = settings.ADMIN_USER)
    token = fields.EncryptedCharField(max_length = 256, default = settings.DEFAULT_ADMIN_TOKEN)
    repo = django.CharField(max_length = 1096, default = settings.DEFAULT_RUNTIME_REPO)
    base_image = django.CharField(max_length = 256, default = settings.DEFAULT_RUNTIME_IMAGE)
    runtime_image = django.CharField(max_length = 256, null = True)

    class Meta(resource.ResourceModel.Meta):
        verbose_name = 'environment'
        verbose_name_plural = 'environments'
        facade_class = EnvironmentFacade
        dynamic_fields = ['is_active']
        ordering = ['name']
        provider_name = 'environment'

    def  __str__(self):
        return "{}".format(self.name)

    def get_id(self):
        return self.name

    @property
    def is_active(self):
        return True if self.name == self.facade.get_env() else False


    def save(self, *args, **kwargs):
        from data.state.models import State
        super().save(*args, **kwargs)

        env_name = Runtime.get_env()
        if self.name == env_name:
            image = self.base_image
            if self.runtime_image:
                image = self.runtime_image

            Runtime.set_env(
                self.name,
                self.repo,
                image
        )
        State.facade.store('env_ensure', value = True)
