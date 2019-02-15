from django.conf import settings

from systems.command import providers

import netaddr
import ipaddress


class SubnetMixin(object):

    def get_cidr(self, instance, config, networks):
        if config['cidr']:
            cidrs = [self.parse_cidr(config['cidr'])]
        else:
            cidrs = self.parse_subnets(
                config['cidr_base'], 
                config['cidr_prefix']
            )
        
        for cidr in cidrs:
            create = True

            for network in networks:
                if instance.name != network.name:
                    if network.cidr and self.overlapping_subnets(cidr, network.cidr):
                        create = False
                        break
            
            if create:
                return str(cidr)
        
        return None

    def parse_cidr(self, cidr):
        cidr = str(cidr)

        if '*' in cidr or '-' in cidr:
            return netaddr.glob_to_cidrs(cidr)[0]
        
        if '/' not in cidr:
            cidr = "{}/32".format(cidr)
        
        return netaddr.IPNetwork(cidr, implicit_prefix = True)

    def parse_subnets(self, cidr, prefix_size):
        return list(self.parse_cidr(str(cidr)).subnet(int(prefix_size)))

    def overlapping_subnets(self, cidr, other_cidr):
        cidr1 = ipaddress.IPv4Network(str(cidr))
        cidr2 = ipaddress.IPv4Network(str(other_cidr))
        return cidr1.overlaps(cidr2)


class NetworkProvider(SubnetMixin, providers.TerraformProvider):
    
    def provider_config(self, type = None):
        self.option(str, 'cidr', None, help = 'Network IPv4 CIDR address (between /16 and /28)')
        self.option(str, 'cidr_base', '10/8', help = 'Network IPv4 root CIDR address (not used if "cidr" option specified)')
        self.option(int, 'cidr_prefix', 16, help = 'Network IPv4 CIDR address prefix size (not used if "cidr" option specified)')
    
    def terraform_type(self):
        return 'network'

    @property
    def facade(self):
        return self.command._network

    def create(self, name, fields):
        fields['type'] = self.name
        return super().create(name, fields)
     
    def initialize_terraform(self, instance, relations, created):
        instance.cidr = self.get_cidr(instance, self.config, self.command.networks)
        if not instance.cidr:
            self.command.error("No available network cidr matches. Try another cidr")


class NetworkPeerProvider(providers.TerraformProvider):
   
    def terraform_type(self):
        return 'network_peer'

    @property
    def facade(self):
        return self.command._network_peer

    def create(self, name, fields, **relations):
        pass

    def update(self, peer_names):
        instance = self.check_instance('network peer update')
        network = self.command._network.retrieve(instance.name)

        peer_names = [ x for x in peer_names if x != instance.name ]
        self.update_related(instance, 'peers', self.command._network, peer_names)

        peers = instance.peers.all()
        self.update_config(instance, network, peers)
        self.initialize_instance(instance, {}, False)

        instance.config = instance.config
        instance.save()
    
    def update_config(self, instance, network, peers):
        pass


class SubnetProvider(SubnetMixin, providers.TerraformProvider):
    
    def provider_config(self, type = None):
        self.option(str, 'cidr', None, help = 'Subnet IPv4 CIDR address (between /16 and /28)')
        self.option(int, 'cidr_prefix', 24, help = 'Subnet IPv4 CIDR address prefix size (not used if "cidr" option specified)')

    def terraform_type(self):
        return 'subnet'

    @property
    def facade(self):
        return self.command._subnet

    def create(self, name, network, fields):
        fields['type'] = self.name
        fields['network'] = network
        return super().create(name, fields)
    
    def initialize_terraform(self, instance, relations, created):
        self.config['cidr_base'] = instance.network.cidr
        instance.cidr = self.get_cidr(instance, self.config, self.command.subnets)
        if not instance.cidr:
            self.command.error("No available subnet cidr matches. Try another cidr")


class FirewallProvider(providers.TerraformProvider):

    def terraform_type(self):
        return 'firewall'

    @property
    def facade(self):
        return self.command._firewall

    def create(self, name, network, fields):
        fields['type'] = self.name
        fields['network'] = network
        return super().create(name, fields)


class FirewallRuleProvider(SubnetMixin, providers.TerraformProvider):
    
    def provider_config(self, type = None):
        self.option(str, 'mode', 'ingress', help = 'Firewall rule mode (ingress | egress)')
        self.option(str, 'protocol', 'tcp', help = 'Firewall rule protocol (tcp | udp | icmp)')
        self.option(int, 'from_port', 0, help = 'Firewall rule from port (at least one "from" or "to" port must be specified)')
        self.option(int, 'to_port', 65535, help = 'Firewall rule to port (at least one "from" or "to" port must be specified)')
        self.option(list, 'cidrs', [], help = 'Firewall rule applicable CIDRs', config_name = 'aws_sgroup_cidrs')

    def terraform_type(self):
        return 'firewall_rule'

    @property
    def facade(self):
        return self.command._firewall_rule

    def create(self, name, firewall, fields):
        fields['type'] = self.name
        fields['firewall'] = firewall
        return super().create(name, fields)
        
    def initialize_terraform(self, instance, relations, created):
        if instance.mode not in ('ingress', 'egress'):
            self.command.error("Firewall rule mode {} is not supported".format(instance.type))
        
        if instance.protocol not in ('tcp', 'udp', 'icmp'):
            self.command.error("Firewall rule protocol {} is not supported".format(instance.protocol))

        if instance.cidrs:
            instance.cidrs = [str(self.parse_cidr(x.strip())) for x in instance.cidrs]
        else:
            instance.cidrs = ['0.0.0.0/0']


class BaseNetworkProvider(providers.MetaCommandProvider):

    def __init__(self, name, command, instance = None):
        super().__init__(name, command, instance)
        self.provider_type = 'network'
        self.provider_options = settings.NETWORK_PROVIDERS
    
    def register_types(self):
        self.set('network', NetworkProvider)
        self.set('network_peer', NetworkPeerProvider)
        self.set('subnet', SubnetProvider)
        self.set('firewall', FirewallProvider)
        self.set('firewall_rule', FirewallRuleProvider)
