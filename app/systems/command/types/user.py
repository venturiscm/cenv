from settings import Roles
from .router import RouterCommand
from .action import ActionCommand


class UserRouterCommand(RouterCommand):

    def get_priority(self):
        return 95


class UserActionCommand(ActionCommand):

    def groups_allowed(self):
        return [
            Roles.admin, 
            Roles.user_admin
        ]

    def server_enabled(self):
        return True
