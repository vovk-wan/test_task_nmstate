import pytest

from models import NetInterface


@pytest.fixture()
def iface():
    """The fixture creates an instance of the NetInterface class for each test."""

    return NetInterface(**{
        "name": "eth0",
        "type": "etherno",
        "state": "up",
        "controller": "fdsfs",
        "ipv4": {"enabled": True, "dhcp": True},
    })


@pytest.fixture()
def net_state() -> dict:
    """The fixture returns the network state by emulating the response of the netstate library"""

    return {
        'hostname': {
            'running': 'localhost.localdomain',
            'config': ''
        },
        'dns-resolver': {
            'running': {
                'server': [
                    '10.0.2.3',
                    '10.0.3.3'
                ],
                'search': []
            },
            'config': {}
        },
        'route-rules': {
            'config': []
        },
        'routes': {
            'running': [
                {
                    'destination': '0.0.0.0/0',
                    'next-hop-interface': 'enp0s3',
                    'next-hop-address': '10.0.2.2',
                    'metric': 101,
                    'table-id': 254,
                    'source': '10.0.2.15'
                },
                {
                    'destination': '0.0.0.0/0',
                    'next-hop-interface': 'br0',
                    'next-hop-address': '10.0.3.2',
                    'metric': 425,
                    'table-id': 254,
                    'source': '10.0.3.15'
                }
            ],
            'config': []
        },
        'interfaces': [
            {
                'name': 'br0',
                'type': 'linux-bridge',
                'state': 'up',
                'identifier': 'name',
                'mac-address': '08:00:27:C8:5E:4A',
                'mtu': 1500,
                'min-mtu': 68,
                'max-mtu': 65535,
                'wait-ip': 'any',
                'ipv4': {
                    'enabled': True,
                    'dhcp': True,
                    'dhcp-client-id': 'll',
                    'address': [
                        {
                            'ip': '10.0.3.15',
                            'prefix-length': 24,
                            'mptcp-flags': [
                                'subflow'
                            ],
                            'valid-life-time': '80447sec',
                            'preferred-life-time': '80447sec'
                        }
                    ],
                    'auto-dns': True,
                    'auto-gateway': True,
                    'auto-routes': True,
                    'auto-route-table-id': 0,
                    'dhcp-send-hostname': True
                },
                'ipv6': {
                    'enabled': False,
                    'dhcp': False,
                    'autoconf': False
                },
                'mptcp': {
                    'address-flags': [
                        'subflow'
                    ]
                },
                'accept-all-mac-addresses': False,
                'lldp': {
                    'enabled': False
                },
                'ethtool': {
                    'feature': {
                        'highdma': False,
                        'rx-gro': True,
                        'rx-gro-list': False,
                        'rx-udp-gro-forwarding': False,
                        'tx-checksum-ip-generic': True,
                        'tx-esp-segmentation': True,
                        'tx-fcoe-segmentation': False,
                        'tx-generic-segmentation': True,
                        'tx-gre-csum-segmentation': True,
                        'tx-gre-segmentation': True,
                        'tx-gso-list': False,
                        'tx-gso-partial': True,
                        'tx-gso-robust': False,
                        'tx-ipxip4-segmentation': True,
                        'tx-ipxip6-segmentation': True,
                        'tx-nocache-copy': False,
                        'tx-scatter-gather-fraglist': False,
                        'tx-sctp-segmentation': False,
                        'tx-tcp-ecn-segmentation': True,
                        'tx-tcp-mangleid-segmentation': True,
                        'tx-tcp-segmentation': True,
                        'tx-tcp6-segmentation': True,
                        'tx-tunnel-remcsum-segmentation': True,
                        'tx-udp-segmentation': False,
                        'tx-udp_tnl-csum-segmentation': True,
                        'tx-udp_tnl-segmentation': True,
                        'tx-vlan-hw-insert': True,
                        'tx-vlan-stag-hw-insert': True
                    }
                },
                'bridge': {
                    'options': {
                        'gc-timer': 3898,
                        'group-addr': '01:80:C2:00:00:00',
                        'group-forward-mask': 0,
                        'group-fwd-mask': 0,
                        'hash-max': 4096,
                        'hello-timer': 122,
                        'mac-ageing-time': 300,
                        'multicast-last-member-count': 2,
                        'multicast-last-member-interval': 100,
                        'multicast-membership-interval': 26000,
                        'multicast-querier': False,
                        'multicast-querier-interval': 25500,
                        'multicast-query-interval': 12500,
                        'multicast-query-response-interval': 1000,
                        'multicast-query-use-ifaddr': False,
                        'multicast-router': 'auto',
                        'multicast-snooping': True,
                        'multicast-startup-query-count': 2,
                        'multicast-startup-query-interval': 3125,
                        'stp': {
                            'enabled': True,
                            'forward-delay': 15,
                            'hello-time': 2,
                            'max-age': 20,
                            'priority': 32768
                        },
                        'vlan-protocol': '802.1q',
                        'vlan-default-pvid': 1
                    },
                    'port': [
                        {
                            'name': 'enp0s8',
                            'stp-hairpin-mode': False,
                            'stp-path-cost': 100,
                            'stp-priority': 32
                        },
                        {
                            'name': 'enp0s9',
                            'stp-hairpin-mode': False,
                            'stp-path-cost': 100,
                            'stp-priority': 32
                        }
                    ]
                }
            },
            {
                'name': 'enp0s10',
                'type': 'ethernet',
                'driver': 'e1000',
                'state': 'down',
                'mac-address': '08:00:27:FA:19:27',
                'permanent-mac-address': '08:00:27:FA:19:27',
                'mtu': 1500,
                'min-mtu': 46,
                'max-mtu': 16110,
                'ipv4': {
                    'enabled': False
                },
                'ipv6': {
                    'enabled': False
                },
                'accept-all-mac-addresses': False,
                'ethtool': {
                    'pause': {
                        'rx': True,
                        'tx': False,
                        'autoneg': True
                    },
                    'feature': {
                        'rx-all': False,
                        'rx-checksum': False,
                        'rx-fcs': False,
                        'rx-gro': True,
                        'rx-gro-list': False,
                        'rx-udp-gro-forwarding': False,
                        'rx-vlan-hw-parse': True,
                        'tx-checksum-ip-generic': True,
                        'tx-generic-segmentation': True,
                        'tx-nocache-copy': False,
                        'tx-tcp-mangleid-segmentation': False,
                        'tx-tcp-segmentation': True
                    },
                    'ring': {
                        'rx': 256,
                        'rx-max': 4096,
                        'tx': 256,
                        'tx-max': 4096
                    }
                },
                'ethernet': {
                    'auto-negotiation': True,
                    'speed': 1000,
                    'duplex': 'full'
                }
            },
            {
                'name': 'enp0s3',
                'type': 'ethernet',
                'driver': 'e1000',
                'state': 'up',
                'identifier': 'name',
                'mac-address': '08:00:27:F6:06:F3',
                'permanent-mac-address': '08:00:27:F6:06:F3',
                'mtu': 1500,
                'min-mtu': 46,
                'max-mtu': 16110,
                'wait-ip': 'any',
                'ipv4': {
                    'enabled': True,
                    'dhcp': True,
                    'address': [
                        {
                            'ip': '10.0.2.15',
                            'prefix-length': 24,
                            'mptcp-flags': [
                                'subflow'
                            ],
                            'valid-life-time': '80415sec',
                            'preferred-life-time': '80415sec'
                        }
                    ],
                    'auto-dns': True,
                    'auto-gateway': True,
                    'auto-routes': True,
                    'auto-route-table-id': 0,
                    'dhcp-send-hostname': True
                },
                'ipv6': {
                    'enabled': True,
                    'dhcp': True,
                    'autoconf': True,
                    'address': [
                        {
                            'ip': 'fe80::a00:27ff:fef6:6f3',
                            'prefix-length': 64
                        }
                    ],
                    'auto-dns': True,
                    'auto-gateway': True,
                    'auto-routes': True,
                    'auto-route-table-id': 0,
                    'addr-gen-mode': 'eui64',
                    'dhcp-send-hostname': True
                },
                'mptcp': {
                    'address-flags': [
                        'subflow'
                    ]
                },
                'accept-all-mac-addresses': False,
                'lldp': {
                    'enabled': False
                },
                'ethtool': {
                    'pause': {
                        'rx': True,
                        'tx': False,
                        'autoneg': True
                    },
                    'feature': {
                        'rx-all': False,
                        'rx-checksum': False,
                        'rx-fcs': False,
                        'rx-gro': True,
                        'rx-gro-list': False,
                        'rx-udp-gro-forwarding': False,
                        'rx-vlan-hw-parse': True,
                        'tx-checksum-ip-generic': True,
                        'tx-generic-segmentation': True,
                        'tx-nocache-copy': False,
                        'tx-tcp-mangleid-segmentation': False,
                        'tx-tcp-segmentation': True
                    },
                    'ring': {
                        'rx': 256,
                        'rx-max': 4096,
                        'tx': 256,
                        'tx-max': 4096
                    }
                },
                'ethernet': {
                    'auto-negotiation': True,
                    'speed': 1000,
                    'duplex': 'full'
                }
            },
            {
                'name': 'enp0s8',
                'type': 'ethernet',
                'driver': 'e1000',
                'state': 'up',
                'identifier': 'name',
                'mac-address': '08:00:27:C8:5E:4A',
                'permanent-mac-address': '08:00:27:C8:5E:4A',
                'mtu': 1500,
                'min-mtu': 46,
                'max-mtu': 16110,
                'ipv4': {
                    'enabled': False
                },
                'ipv6': {
                    'enabled': False
                },
                'controller': 'br0',
                'accept-all-mac-addresses': False,
                'lldp': {
                    'enabled': False
                },
                'ethtool': {
                    'pause': {
                        'rx': True,
                        'tx': False,
                        'autoneg': True
                    },
                    'feature': {
                        'rx-all': False,
                        'rx-checksum': False,
                        'rx-fcs': False,
                        'rx-gro': True,
                        'rx-gro-list': False,
                        'rx-udp-gro-forwarding': False,
                        'rx-vlan-hw-parse': True,
                        'tx-checksum-ip-generic': True,
                        'tx-generic-segmentation': True,
                        'tx-nocache-copy': False,
                        'tx-tcp-mangleid-segmentation': False,
                        'tx-tcp-segmentation': True
                    },
                    'ring': {
                        'rx': 256,
                        'rx-max': 4096,
                        'tx': 256,
                        'tx-max': 4096
                    }
                },
                'ethernet': {
                    'auto-negotiation': True,
                    'speed': 1000,
                    'duplex': 'full'
                }
            },
            {
                'name': 'enp0s9',
                'type': 'ethernet',
                'driver': 'e1000',
                'state': 'down',
                'mac-address': '08:00:27:89:A6:71',
                'permanent-mac-address': '08:00:27:89:A6:71',
                'mtu': 1500,
                'min-mtu': 46,
                'max-mtu': 16110,
                'ipv4': {
                    'enabled': False
                },
                'ipv6': {
                    'enabled': False
                },
                'accept-all-mac-addresses': False,
                'ethtool': {
                    'pause': {
                        'rx': True,
                        'tx': False,
                        'autoneg': True
                    },
                    'feature': {
                        'rx-all': False,
                        'rx-checksum': False,
                        'rx-fcs': False,
                        'rx-gro': True,
                        'rx-gro-list': False,
                        'rx-udp-gro-forwarding': False,
                        'rx-vlan-hw-parse': True,
                        'tx-checksum-ip-generic': True,
                        'tx-generic-segmentation': True,
                        'tx-nocache-copy': False,
                        'tx-tcp-mangleid-segmentation': False,
                        'tx-tcp-segmentation': True
                    },
                    'ring': {
                        'rx': 256,
                        'rx-max': 4096,
                        'tx': 256,
                        'tx-max': 4096
                    }
                },
                'ethernet': {
                    'auto-negotiation': True,
                    'speed': 1000,
                    'duplex': 'full'
                }
            },
            {
                'name': 'lo',
                'type': 'loopback',
                'state': 'up',
                'mac-address': '00:00:00:00:00:00',
                'mtu': 65536,
                'ipv4': {
                    'enabled': True,
                    'address': [
                        {
                            'ip': '127.0.0.1',
                            'prefix-length': 8
                        }
                    ]
                },
                'ipv6': {
                    'enabled': True,
                    'address': [
                        {
                            'ip': '::1',
                            'prefix-length': 128
                        }
                    ]
                },
                'accept-all-mac-addresses': False,
                'ethtool': {
                    'feature': {
                        'rx-gro': True,
                        'rx-gro-list': False,
                        'rx-udp-gro-forwarding': False,
                        'tx-generic-segmentation': True,
                        'tx-gso-list': True,
                        'tx-sctp-segmentation': True,
                        'tx-tcp-ecn-segmentation': True,
                        'tx-tcp-mangleid-segmentation': True,
                        'tx-tcp-segmentation': True,
                        'tx-tcp6-segmentation': True,
                        'tx-udp-segmentation': True
                    }
                }
            }
        ]
    }
