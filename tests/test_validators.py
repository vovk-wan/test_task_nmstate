"""
test_validators.py
------------------
Tests for validators.
"""

import pytest

from validators import ipv4_validator, bridge_name_validator


@pytest.mark.parametrize("ip, expected", [
    ("192.168.1.1", True),
    ("255.255.255.255", True),
    ("0.0.0.0", True),
    ("256.1.1.1", False),
    ("192.168.1", False),
    ("192.168.1.1.1", False),
    ("a.b.c.d", False),
    ("", False),
    (None, False),
])
def test_validate_ipv4(ip, expected):
    assert ipv4_validator(value=ip) == expected


@pytest.mark.parametrize("name, expected", [
    ("b", True),
    ("br1", True),
    ("w343nfjl4kfgw32", True),
    ("q12js", True),
    ("1", False),
    ("qazwsxedcrfvtgby", False),
    ("1name", False),
    ("", False),
    (None, False),
])
def test_bridge_name_validator(name, expected):
    assert bridge_name_validator(value=name) == expected
