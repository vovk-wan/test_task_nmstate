"""
test_netinterface_model.py
--------------------------
module for NetInterface class tests
"""

from unittest.mock import patch

import libnmstate
import pytest

from models import NetInterface


def test_initialization_error():
    """Test exception during NetInterface initialization"""

    with pytest.raises(TypeError):
        NetInterface(**{})


def test_state_up(iface):
    """Method state_up test"""

    res = iface.state_up()
    assert iface.name == res["name"]
    assert res["state"] == "up"


def test_state_down(iface):
    """Method state_down test"""

    res = iface.state_down()
    assert iface.name == res["name"]
    assert res["state"] == "down"


def test_dhcp_up(iface):
    """Method dhcp_up test"""

    res = iface.dhcp_up()
    assert iface.name == res["name"]
    assert res["state"] == "up"
    assert res["ipv4"]["enabled"] is True
    assert res["ipv4"]["dhcp"] is True


def test_dhcp_down(iface):
    """Method dhcp_down test"""

    ip = "10.0.2.10"
    res = iface.dhcp_down(ip)
    assert iface.name == res["name"]
    assert res["state"] == "up"
    assert res["ipv4"]["enabled"] is True
    assert res["ipv4"]["dhcp"] is False
    assert res["ipv4"]["address"][0]["ip"] == ip


def test_add_bridge(iface):
    """Method dhcp_down test"""

    bridge_name = "br0"
    res = iface.add_bridge(bridge_name)
    assert iface.name == res["name"]
    assert res["state"] == "up"
    assert res["controller"] == bridge_name


def test_update_bridges(iface):
    """Method update_bridges test"""

    bridge_name = "br0"
    iface.update_bridges(bridge_name)
    assert iface.bridges
    bridges = [b for b in iface.bridges if b["name"] == bridge_name]
    assert len(bridges) == 1
    bridge = bridges[0]
    assert bridge["type"] == "linux-bridge"
    assert bridge["state"] == "up"
    assert bridge["ipv4"]["enabled"] is True
    assert bridge["ipv4"]["dhcp"] is True
    ports = bridge["bridge"]["port"]
    assert len(ports) > 0
    assert bool([p for p in ports if p["name"] == iface.name])


def test_serialize(iface):
    """Method serialize test"""

    expected = [
        {'name': 'state', 'value': 'up', 'type': 'state_bool'},
        {'name': 'ipv4 dhcp', 'value': True, 'type': 'bool'},
        {'name': 'ipv4 address', 'value': '', 'type': 'ipv4address'},
        {'name': 'bridge', 'value': True, 'type': 'bool'},
        {'name': 'bridge name', 'value': 'fdsfs', 'type': 'bridge_name'},
        {'name': 'apply', 'value': iface.apply, 'type': 'apply_button'}
    ]
    res = iface.serialize()
    print(res)
    assert res == expected


def test_update_interfaces(iface, net_state):
    """Method update_interfaces test"""

    with patch('libnmstate.show') as mock_show:
        mock_show.return_value = net_state
        iface.update_interfaces()

    assert len(iface.bridges) == 1
    assert len(iface.ethernet_interfaces) == 4


def test_get_interfaces(net_state):
    """Method get_interfaces test"""

    interfaces = NetInterface.get_interfaces(net_state)
    assert len(interfaces) == 6


def test_get_bridge_ports(iface, net_state):
    """Method get_bridge_ports test"""

    interfaces = net_state["interfaces"]
    bridges = [i for i in interfaces if i["type"] == "linux-bridge"]
    bridge = bridges[0]
    ports = iface.get_bridge_ports(bridge)
    assert len(ports) == len(bridge["bridge"]["port"])
