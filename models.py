from dataclasses import dataclass
import logging

import libnmstate
from libnmstate.schema import (Interface, InterfaceState, InterfaceIPv4, LinuxBridge, InterfaceType)
from libnmstate.error import NmstateError

logging.getLogger('libnmstate').propagate = False
logging.getLogger('libnmstate').addHandler(logging.NullHandler())
logging.getLogger('urllib3').propagate = False
logging.getLogger('requests').propagate = False


class NetInterface:
    """
    Класс - оболочка ethernet интерфейса
    """
    net_state = dict()
    ethernet_interfaces = list()
    bridges = list()

    def __init__(self, **kwargs):
        self.name = kwargs[Interface.NAME]
        self.type = kwargs[Interface.TYPE]
        self.state = kwargs[Interface.STATE]
        self.mac_address = kwargs[Interface.MAC]
        self.mtu = kwargs[Interface.MTU]
        self.controller = kwargs.get(Interface.CONTROLLER, '')
        self.ipv4 = kwargs[Interface.IPV4]
        self.ipv6 = kwargs[Interface.IPV6]

    def state_up(self) -> dict:
        return {
            Interface.NAME: self.name,
            Interface.STATE: InterfaceState.UP
        }

    def state_down(self) -> dict:
        return {
            Interface.NAME: self.name,
            Interface.STATE: InterfaceState.DOWN
        }

    def dhcp_up(self) -> dict:
        return {
                    Interface.NAME: self.name,
                    Interface.TYPE: InterfaceType.ETHERNET,
                    Interface.STATE: InterfaceState.UP,
                    Interface.IPV4: {
                        InterfaceIPv4.ENABLED: True,
                        InterfaceIPv4.DHCP: True,
                    }
                }

    def dhcp_down(self, ip) -> dict:
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
        return {
            Interface.NAME: self.name,
            Interface.TYPE: InterfaceType.ETHERNET,
            Interface.STATE: InterfaceState.UP,
            Interface.CONTROLLER: bridge,
        }

    def _create_bridge(self, bridge: str) -> None:
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
                    LinuxBridge.PORT_SUBTREE: [
                        {LinuxBridge.Port.NAME: self.name}
                    ]
                },
            }
        )

    def _add_bridge(self, bridge: str) -> None:
        if not bridge:
            return
        for item in self.bridges:
            if item[Interface.NAME] == bridge:
                ports = [
                    port for port in item.get(LinuxBridge.CONFIG_SUBTREE, {}).get(LinuxBridge.PORT_SUBTREE, [])
                ]
                ports.append({LinuxBridge.Port.NAME: self.name})
                item[LinuxBridge.CONFIG_SUBTREE] = {LinuxBridge.PORT_SUBTREE: ports}
                return
        self._create_bridge(bridge)

    def _remove_bridge(self) -> None:

        for item in self.bridges:
            if item[Interface.NAME] == self.controller:
                ports = [
                    port for port in item.get(LinuxBridge.CONFIG_SUBTREE, {}).get(LinuxBridge.PORT_SUBTREE, [])
                    if port["name"] != self.name
                ]
                item[LinuxBridge.CONFIG_SUBTREE] = {LinuxBridge.PORT_SUBTREE: ports}
                break

    def update_bridges(self, bridge: str) -> None:
        if self.controller == bridge:
            return
        self._add_bridge(bridge)
        if self.controller:
            self._remove_bridge()
        # 1 есть новый мост, был старый мост
        # if bridge and self.controller:
        #     for item in self.bridges:
        #         if item[Interface.NAME] == bridge:
        #             ports = [
        #                 port for port in item.get(LinuxBridge.CONFIG_SUBTREE, {}).get(LinuxBridge.PORT_SUBTREE, [])
        #             ]
        #             ports.append({LinuxBridge.Port.NAME: self.name})
        #             item[LinuxBridge.CONFIG_SUBTREE] = {LinuxBridge.PORT_SUBTREE: ports}
        #             break
        #     else:
        #         self.bridges.append(
        #             {
        #                 Interface.NAME: bridge,
        #                 Interface.TYPE: InterfaceType.LINUX_BRIDGE,
        #                 Interface.STATE: InterfaceState.UP,
        #                 Interface.IPV4: {
        #                     InterfaceIPv4.ENABLED: True,
        #                     InterfaceIPv4.DHCP: True,
        #                 },
        #                 LinuxBridge.CONFIG_SUBTREE: {
        #                     LinuxBridge.PORT_SUBTREE: [
        #                         {LinuxBridge.Port.NAME: self.name}
        #                     ]
        #                 },
        #             }
        #         )

            # for item in self.bridges:
            #     if item[Interface.NAME] == self.controller:
            #         ports = [
            #             port for port in item.get(LinuxBridge.CONFIG_SUBTREE, {}).get(LinuxBridge.PORT_SUBTREE, [])
            #             if port["name"] != self.name
            #         ]
            #         item[LinuxBridge.CONFIG_SUBTREE] = {LinuxBridge.PORT_SUBTREE: ports}
            #         break

        # 2 есть новый мост, не было старого моста
        # if bridge and not self.controller:
        #     for item in self.bridges:
        #         if item[Interface.NAME] == bridge:
        #             ports = [
        #                 port for port in item.get(LinuxBridge.CONFIG_SUBTREE, {}).get(LinuxBridge.PORT_SUBTREE, [])
        #             ]
        #             ports.append({LinuxBridge.Port.NAME: self.name})
        #             item[LinuxBridge.CONFIG_SUBTREE] = {LinuxBridge.PORT_SUBTREE: ports}
        #             break
        #     else:
        #         self.bridges.append(
        #             {
        #                 Interface.NAME: bridge,
        #                 Interface.TYPE: InterfaceType.LINUX_BRIDGE,
        #                 Interface.STATE: InterfaceState.UP,
        #                 Interface.IPV4: {
        #                     InterfaceIPv4.ENABLED: True,
        #                     InterfaceIPv4.DHCP: True,
        #                 },
        #                 LinuxBridge.CONFIG_SUBTREE: {
        #                     LinuxBridge.PORT_SUBTREE: [
        #                         {LinuxBridge.Port.NAME: self.name}
        #                     ]
        #                 },
        #             }
        #         )

        # 3 был старый мост нет нового
        # if not bridge and self.controller:
        #     for item in self.bridges:
        #         if item[Interface.NAME] == self.controller:
        #             ports = [
        #                 port for port in item.get(LinuxBridge.CONFIG_SUBTREE, {}).get(LinuxBridge.PORT_SUBTREE, [])
        #                 if port[LinuxBridge.Port.NAME] != self.name
        #             ]
        #             item[LinuxBridge.CONFIG_SUBTREE] = {LinuxBridge.PORT_SUBTREE: ports}
        #             break

    def apply(self, **kwargs):
        self.get_interfaces()
        orig = {item["name"]: item["value"] for item in self.serialize() if item["name"] in kwargs}
        if orig == kwargs:
            return 'no changes'
        iface = []
        bridge_name = ''

        if "state" in kwargs and kwargs["state"].lower() == "down":
            iface = self.state_down()
        elif "ipv4 address" in kwargs:
            iface = self.dhcp_down(kwargs["ipv4 address"])
        elif "ipv4 dhcp" in kwargs and kwargs["ipv4 dhcp"]:
            iface = self.dhcp_up()
        elif "bridge name" in kwargs and kwargs["bridge name"]:
            bridge_name = kwargs["bridge name"]
            iface = self.add_bridge(kwargs["bridge name"])

        self.update_bridges(bridge_name)

        state = {
             Interface.KEY: [
                 *self.bridges,
                 iface
             ]
        }
        # return str(state)
        if state[Interface.KEY]:
            try:
                libnmstate.apply(state, verify_change=True, rollback_timeout=30)
                return "Ok"
            except NmstateError as e:
                return str(e)

    def __str__(self):
        ip4_address = []
        if 'address' in self.ipv4.keys():
            ip4_address = [address[InterfaceIPv4.ADDRESS_IP] for address in self.ipv4[InterfaceIPv4.ADDRESS]]
        return (
            f'name {self.name} \n '
            f'type  {self.type},\n '
            f'ip4 address {ip4_address},\n '
            f'state {self.state},\n '
                )

    def serialize(self) -> list[dict]:  # TODO может стоит заменить использовать `маппер` изменения вносить в интерфейс
        groups = list()
        groups.append(dict(name="state", value=self.state, type="state_bool"))
        # groups.append(dict(name="ipv4 enabled", value=self.ipv4[InterfaceIPv4.ENABLED], type="bool"))
        dhcp = self.ipv4[InterfaceIPv4.DHCP] if self.ipv4[InterfaceIPv4.ENABLED] else False
        groups.append(dict(name="ipv4 dhcp", value=dhcp, type="bool"))
        address = ''
        if self.state == InterfaceState.UP:
            if 'addresfdsfs' in self.ipv4.keys():
                address = self.ipv4[InterfaceIPv4.ADDRESS][0][InterfaceIPv4.ADDRESS_IP]

        groups.append(dict(name="ipv4 address", value=address, type="ipv4address"))
        groups.append(dict(name="bridge", value=bool(self.controller), type="bool"))
        groups.append(dict(name="bridge name", value=self.controller, type="bridge_name"))
        groups.append(dict(name="apply", value=self.apply if self.controller else '', type="apply_button"))

        return groups

    @classmethod
    def get_interfaces(cls, force: bool = False) -> None:
        if force or not cls.net_state:
            cls.net_state = libnmstate.show()
        cls.ethernet_interfaces = [
            NetInterface(**interface) for interface in cls.net_state[Interface.KEY]
            if interface[Interface.TYPE] == InterfaceType.ETHERNET
        ]
        cls.bridges = []
        for interface in [interface for interface in cls.net_state[Interface.KEY]
                          if interface[Interface.TYPE] == InterfaceType.LINUX_BRIDGE]:
            ports = [
                {LinuxBridge.Port.NAME: port.get(LinuxBridge.Port.NAME)}
                for port in interface.get(LinuxBridge.CONFIG_SUBTREE, {}).get(LinuxBridge.PORT_SUBTREE, [])
            ]

            cls.bridges.append(
                {
                    Interface.NAME: interface[Interface.NAME],
                    Interface.TYPE: InterfaceType.LINUX_BRIDGE,
                    Interface.STATE: InterfaceState.UP,
                    Interface.IPV4: {
                        InterfaceIPv4.ENABLED: True,
                        InterfaceIPv4.DHCP: True,
                    },
                    LinuxBridge.CONFIG_SUBTREE: {
                        LinuxBridge.PORT_SUBTREE: [*ports]
                    },
                }
            )


def get_all_interfaces():
    data = libnmstate.show()
    return [NetInterface(**interface) for interface in data['interfaces']]


def get_ethernet_interfaces():
    data = libnmstate.show()
    return [
        NetInterface(**interface) for interface in data['interfaces']
        if interface[Interface.TYPE] == InterfaceType.ETHERNET
    ]

#
# @dataclass
# class InterfaceItem:  # TODO удалить, это лишнее
#     interface: NetInterface
#     name: str

# TODO
# TODO 1 docstring
# TODO 2 annotation
# TODO 3 review
# TODO 4 linters (flake8 + blake)
