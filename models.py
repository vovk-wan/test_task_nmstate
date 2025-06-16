"""
models.py
---------
The module contains classes and methods for the application to work with the nmstate library.
"""

import logging

import libnmstate

from libnmstate.schema import (
    Interface,
    InterfaceState,
    InterfaceIPv4,
    LinuxBridge,
    InterfaceType,
)
from libnmstate.error import NmstateError

APPLY_RESULT_NO_CHANGE = "no change"
APPLY_RESULT_OK = "Ok"


logging.getLogger("libnmstate").propagate = False
logging.getLogger("libnmstate").addHandler(logging.NullHandler())
logging.getLogger("urllib3").propagate = False
logging.getLogger("requests").propagate = False


class NetInterface:
    """Class - ethernet interface wrapper."""

    net_state = dict()
    ethernet_interfaces = list()
    bridges = list()

    def __init__(self, **kwargs):
        self.name = kwargs[Interface.NAME]
        self.type = kwargs[Interface.TYPE]
        self.state = kwargs[Interface.STATE]
        self.mac_address = kwargs[Interface.MAC]
        self.mtu = kwargs[Interface.MTU]
        self.controller = kwargs.get(Interface.CONTROLLER, "")
        self.ipv4 = kwargs[Interface.IPV4]
        self.ipv6 = kwargs[Interface.IPV6]

    def state_up(self) -> dict:
        """
        The method generates the 'state=up' interface state for the netstate lib.

        Returns: interface state
        """

        return {Interface.NAME: self.name, Interface.STATE: InterfaceState.UP}

    def state_down(self) -> dict:
        """
        Method generates interface state 'state=down' for netstate lib.

        Returns: interface state
        """

        return {Interface.NAME: self.name, Interface.STATE: InterfaceState.DOWN}

    def dhcp_up(self) -> dict:
        """
        Method generates interface state 'dhcp=up' for netstate lib.

        Returns: interface state
        """

        return {
            Interface.NAME: self.name,
            Interface.TYPE: InterfaceType.ETHERNET,
            Interface.STATE: InterfaceState.UP,
            Interface.IPV4: {
                InterfaceIPv4.ENABLED: True,
                InterfaceIPv4.DHCP: True,
            },
        }

    def dhcp_down(self, ip) -> dict:
        """
        The method generates the interface state with manual IP input for the netstate lib.

        Args:
            ip: ip addres

        Returns: interface state
        """

        return {
            Interface.NAME: self.name,
            Interface.STATE: InterfaceState.UP,
            Interface.IPV4: {
                InterfaceIPv4.ENABLED: True,
                InterfaceIPv4.ADDRESS: [
                    {
                        InterfaceIPv4.ADDRESS_IP: ip,
                        InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
                    },
                ],
                InterfaceIPv4.DHCP: False,
            },
        }

    def add_bridge(self, bridge: str) -> dict:
        """
        The method generates the interface state with the LinuxBridge controller for netstat lib.

        Args:
            bridge: bridge name

        Returns: interface state
        """

        return {
            Interface.NAME: self.name,
            Interface.TYPE: InterfaceType.ETHERNET,
            Interface.STATE: InterfaceState.UP,
            Interface.CONTROLLER: bridge,
        }

    def _create_bridge(self, bridge: str) -> None:
        """
        The method adds the LinuxBridge configuration for the netstate library
        to the list of bridges.
        Args:
            bridge: bridge name
        """

        self.bridges.append(
            {
                Interface.NAME: bridge,
                Interface.TYPE: InterfaceType.LINUX_BRIDGE,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV4: {
                    InterfaceIPv4.ENABLED: True,
                    InterfaceIPv4.DHCP: True,
                },
                LinuxBridge.CONFIG_SUBTREE: {
                    LinuxBridge.PORT_SUBTREE: [{LinuxBridge.Port.NAME: self.name}]
                },
            }
        )

    def _add_bridge(self, bridge: str) -> None:
        """
        The method modifies or adds a bridge configuration for the netstate lib
        to the list of bridges.
        Args:
            bridge: bridge name
        """

        if not bridge:
            return
        for item in self.bridges:
            if item[Interface.NAME] == bridge:
                ports = [
                    port
                    for port in item.get(LinuxBridge.CONFIG_SUBTREE, {}).get(
                        LinuxBridge.PORT_SUBTREE, []
                    )
                ]
                ports.append({LinuxBridge.Port.NAME: self.name})
                item[LinuxBridge.CONFIG_SUBTREE] = {LinuxBridge.PORT_SUBTREE: ports}
                return
        self._create_bridge(bridge)

    def _remove_bridge(self) -> None:
        """The method removes a port from the bridge configuration for the netstate lib."""

        for item in self.bridges:
            if item[Interface.NAME] == self.controller:
                ports = [
                    port
                    for port in item.get(LinuxBridge.CONFIG_SUBTREE, {}).get(
                        LinuxBridge.PORT_SUBTREE, []
                    )
                    if port["name"] != self.name
                ]
                item[LinuxBridge.CONFIG_SUBTREE] = {LinuxBridge.PORT_SUBTREE: ports}
                break

    def update_bridges(self, bridge: str) -> None:
        """
        The method updates the bridge configuration for the netstate lib in the bridge list.

        Args:
            bridge: bridge name
        """

        if self.controller == bridge:
            return
        self._add_bridge(bridge)
        if self.controller:
            self._remove_bridge()

    def _get_new_iface_state(self, **kwargs) -> dict:
        """
        The method generates a new interface state for the netstate lib.

        Args:
            **kwargs:

        Returns: interface state
        """

        if "state" in kwargs and kwargs["state"].lower() == "down":
            return self.state_down()
        elif "ipv4 address" in kwargs:
            return self.dhcp_down(kwargs["ipv4 address"])
        elif "ipv4 dhcp" in kwargs and kwargs["ipv4 dhcp"]:
            return self.dhcp_up()
        elif "bridge name" in kwargs and kwargs["bridge name"]:
            return self.add_bridge(kwargs["bridge name"])
        return {}

    def apply(self, **kwargs) -> str:
        """
        The method applies the interface state using the netstate lib.

        Args:
            **kwargs:

        Returns: result apply
        """

        self.update_interfaces()
        origin = {
            item["name"]: item["value"]
            for item in self.serialize()
            if item["name"] in kwargs
        }
        if origin == kwargs:
            return APPLY_RESULT_NO_CHANGE

        iface = self._get_new_iface_state(**kwargs)

        if not iface:
            return APPLY_RESULT_NO_CHANGE

        bridge_name = kwargs.get("bridge name", "") or ""

        self.update_bridges(bridge_name)

        state = {Interface.KEY: [*self.bridges, iface]}
        try:
            libnmstate.apply(state, verify_change=True, rollback_timeout=30)
            return APPLY_RESULT_OK
        except NmstateError as e:
            return str(e)

    def __str__(self):
        ip4_address = []
        if "address" in self.ipv4.keys():
            ip4_address = [address[InterfaceIPv4.ADDRESS_IP] for address in self.ipv4[InterfaceIPv4.ADDRESS]]
        return (
            f"name {self.name} \n "
            f"type  {self.type},\n "
            f"ip4 address {ip4_address},\n "
            f"state {self.state},\n "
        )

    def serialize(self) -> list[dict]:
        """
        The method generates items to represent the interface.

        Returns: list items for view classes
        """

        items = list()
        items.append(dict(name="state", value=self.state, type="state_bool"))

        dhcp = (self.ipv4[InterfaceIPv4.DHCP] if self.ipv4[InterfaceIPv4.ENABLED] else False)
        items.append(dict(name="ipv4 dhcp", value=dhcp, type="bool"))

        address = ""
        if self.state == InterfaceState.UP:
            if InterfaceIPv4.ADDRESS in self.ipv4.keys():
                address = self.ipv4[InterfaceIPv4.ADDRESS][0][InterfaceIPv4.ADDRESS_IP]

        items.append(dict(name="ipv4 address", value=address, type="ipv4address"))
        items.append(dict(name="bridge", value=bool(self.controller), type="bool"))
        items.append(dict(name="bridge name", value=self.controller, type="bridge_name"))
        items.append(dict(name="apply", value=self.apply if self.controller else "", type="apply_button"))

        return items

    @classmethod
    def update_interfaces(cls) -> None:
        """The method updates the list of Ethernet interfaces, the list of bridges, and network state information."""

        cls.net_state = libnmstate.show()
        interfaces = cls.get_interfaces(cls.net_state)

        cls.ethernet_interfaces = [
            NetInterface(**interface) for interface in interfaces
            if interface[Interface.TYPE] == InterfaceType.ETHERNET
        ]

        bridge_interfaces = [
            interface for interface in cls.net_state[Interface.KEY]
            if interface[Interface.TYPE] == InterfaceType.LINUX_BRIDGE
        ]

        cls.bridges = []
        for bridge in bridge_interfaces:
            ports = cls.get_bridge_ports(bridge)

            cls.bridges.append(
                {
                    Interface.NAME: bridge[Interface.NAME],
                    Interface.TYPE: InterfaceType.LINUX_BRIDGE,
                    Interface.STATE: InterfaceState.UP,
                    Interface.IPV4: {
                        InterfaceIPv4.ENABLED: True,
                        InterfaceIPv4.DHCP: True,
                    },
                    LinuxBridge.CONFIG_SUBTREE: {LinuxBridge.PORT_SUBTREE: [*ports]},
                }
            )

    @staticmethod
    def get_interfaces(net_state: dict) -> list:
        """The method returns interfaces from net state."""
        return net_state[Interface.KEY]

    @staticmethod
    def get_bridge_ports(bridge: dict) -> list[dict]:
        """The method returns bridge ports from bridge interface."""
        ports = bridge.get(LinuxBridge.CONFIG_SUBTREE, {}).get(LinuxBridge.PORT_SUBTREE, [])
        return [{LinuxBridge.Port.NAME: port.get(LinuxBridge.Port.NAME)} for port in ports]
