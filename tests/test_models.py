import pytest

from models import NetInterface


net_states = {
    "ok_state": {
        "name": "eth0",
        "type": "etherno",
        "state": "up",
        "controller": "fdsfs",
        "ipv4": {"enabled": True, "dhcp": True},
    },
    "typeerror_state": {}
}


class TestNetInterface:
    """Тесты для класса NetInterface"""

    @pytest.fixture
    def iface(self):
        """The fixture creates an instance of the NetInterface class for each test."""
        return NetInterface(**net_states.get("ok_state"))

    def test_initialization_error(self):
        """Test exception during NetInterface initialization"""
        with pytest.raises(TypeError):
            NetInterface(**net_states.get("typeerror_state"))

    def test_state_up(self, iface):
        """Method state_up test"""

        res = iface.state_up()
        assert iface.name == res["name"]
        assert res["state"] == "up"

    def test_state_down(self, iface):
        """Method state_down test"""

        res = iface.state_down()
        assert iface.name == res["name"]
        assert res["state"] == "down"

    def test_dhcp_up(self, iface):
        """Method dhcp_up test"""

        res = iface.dhcp_up()
        assert iface.name == res["name"]
        assert res["state"] == "up"
        assert res["ipv4"]["enabled"] is True
        assert res["ipv4"]["dhcp"] is True

    def test_dhcp_down(self, iface):
        """Method dhcp_down test"""
        ip = "10.0.2.10"
        res = iface.dhcp_down(ip)
        assert iface.name == res["name"]
        assert res["state"] == "up"
        assert res["ipv4"]["enabled"] is True
        assert res["ipv4"]["dhcp"] is False
        assert res["ipv4"]["address"][0]["ip"] == ip

    def test_add_bridge(self, iface):
        """Method dhcp_down test"""
        bridge_name = "br0"
        res = iface.add_bridge(bridge_name)
        assert iface.name == res["name"]
        assert res["state"] == "up"
        assert res["controller"] == bridge_name

    def test_update_bridges(self, iface):
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

    def test_serialize(self, iface):
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
