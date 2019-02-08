from systems.command import types, mixins


class UpdateCommand(
    types.ServerActionCommand
):
    def get_description(self, overview):
        if overview:
            return """update existing servers in current environment

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam 
pulvinar nisl ac magna ultricies dignissim. Praesent eu feugiat 
elit. Cras porta magna vel blandit euismod.
"""
        else:
            return """update existing servers in current environment
                      
Etiam mattis iaculis felis eu pharetra. Nulla facilisi. 
Duis placerat pulvinar urna et elementum. Mauris enim risus, 
mattis vel risus quis, imperdiet convallis felis. Donec iaculis 
tristique diam eget rutrum.

Etiam sit amet mollis lacus. Nulla pretium, neque id porta feugiat, 
erat sapien sollicitudin tellus, vel fermentum quam purus non sem. 
Mauris venenatis eleifend nulla, ac facilisis nulla efficitur sed. 
Etiam a ipsum odio. Curabitur magna mi, ornare sit amet nulla at, 
scelerisque tristique leo. Curabitur ut faucibus leo, non tincidunt 
velit. Aenean sit amet consequat mauris.
"""
    def parse(self):
        self.parse_test()
        self.parse_network_name('--network')
        self.parse_firewall_names('--firewalls')
        self.parse_server_groups('--groups')
        self.parse_server_reference()
        self.parse_server_fields(True, self.get_provider('compute', 'help').field_help)

    def exec(self):
        self.set_firewall_scope()
        self.set_server_scope()

        def update_server(server, state):
            server.provider.update(
                self.server_fields,
                groups = self.server_group_names,
                firewalls = self.firewall_names
            )         
        self.run_list(self.servers, update_server)
