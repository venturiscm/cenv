from settings.roles import Roles
from .router import RouterCommand
from .action import ActionCommand


class GroupRouterCommand(RouterCommand):

    def get_priority(self):
        return 80


class GroupActionCommand(ActionCommand):

    def groups_allowed(self):
        return [
            Roles.admin,
            Roles.user_admin,
            Roles.config_admin
        ]

    def server_enabled(self):
        return True

    def get_priority(self):
        return 80
