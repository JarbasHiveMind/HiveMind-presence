"""Unit coverage for LocalPresence / LocalDiscovery transport wiring.

These exercise the object graph without any network exchange, so they run fast
and without the hivescope hive or a live LAN.
"""
import pytest

from hivemind_presence.presence import LocalPresence
from hivemind_presence.discovery import LocalDiscovery


def test_presence_defaults_to_no_upnp():
    p = LocalPresence()
    assert p.upnp is None


def test_presence_zeroconf_only_has_no_upnp():
    p = LocalPresence(upnp=False, zeroconf=True)
    assert p.upnp is None
    assert p.zero is not None  # zeroconf installed via [test]


def test_presence_upnp_only_has_no_zeroconf_announce():
    p = LocalPresence(upnp=True, zeroconf=False)
    assert p.upnp is not None
    assert p.zero is None


def test_discovery_zeroconf_only_has_no_upnp():
    d = LocalDiscovery(upnp=False, zeroconf=True)
    assert d.upnp is None
    assert d.zero is not None


def test_discovery_requires_at_least_one_transport():
    with pytest.raises(ValueError):
        LocalDiscovery(upnp=False, zeroconf=False)


def test_discovery_nodes_starts_empty():
    d = LocalDiscovery(upnp=False, zeroconf=True)
    assert d.nodes == {}
