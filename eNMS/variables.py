from json import load
from napalm._SUPPORTED_DRIVERS import SUPPORTED_DRIVERS
from netmiko.ssh_dispatcher import CLASS_MAPPER
from pathlib import Path
from warnings import warn

try:
    from scrapli import Scrapli

    CORE_PLATFORM_MAP = {driver: driver for driver in Scrapli.CORE_PLATFORM_MAP}
except ImportError as exc:
    CORE_PLATFORM_MAP = {"cisco_iosxe": "cisco_iosxe"}
    warn(f"Couldn't import scrapli module ({exc})")


class VariableStore(dict):
    def __init__(self):
        self.load_setup_variables()
        self.load_automation_variables()

    def __setattr__(self, key, value):
        self[key] = value

    def load_setup_variables(self):
        for setup_file in (Path.cwd() / "setup").iterdir():
            with open(setup_file, "r") as file:
                setattr(self, setup_file.stem, load(file))

    def load_automation_variables(self):
        self.netmiko_drivers = sorted((driver, driver) for driver in CLASS_MAPPER)
        self.napalm_drivers = sorted(
            (driver, driver) for driver in SUPPORTED_DRIVERS[1:]
        )
        self.napalm_getters = (
            ("get_arp_table", "ARP table"),
            ("get_bgp_config", "BGP configuration"),
            ("get_bgp_neighbors", "BGP neighbors"),
            ("get_config", "Configuration"),
            ("get_environment", "Environment"),
            ("get_facts", "Facts"),
            ("get_interfaces", "Interfaces"),
            ("get_interfaces_counters", "Interfaces counters"),
            ("get_interfaces_ip", "Interface IP"),
            ("get_ipv6_neighbors_table", "IPv6"),
            ("get_lldp_neighbors", "LLDP neighbors"),
            ("get_lldp_neighbors_detail", "LLDP neighbors detail"),
            ("get_mac_address_table", "MAC address"),
            ("get_network_instances", "Network instances (VRF)"),
            ("get_ntp_peers", "NTP peers"),
            ("get_ntp_servers", "NTP servers"),
            ("get_ntp_stats", "NTP statistics"),
            ("get_optics", "Transceivers"),
            ("get_snmp_information", "SNMP"),
            ("get_users", "Users"),
            ("is_alive", "Is alive"),
        )
        self.scrapli_drivers = CORE_PLATFORM_MAP


locals().update(VariableStore())
