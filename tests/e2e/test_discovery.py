"""Real LAN advertise <-> discover end-to-end tests.

Unlike ``test_presence.py`` (which drives connection-presence through an
in-process hivescope hive), these tests exercise this package's own reason to
exist: a node advertises itself on the local network and a second, independent
discovery client finds it and reads back the announced connection parameters.

The zeroconf/mDNS exchange is real — two independent ``Zeroconf`` stacks talk
over the loopback/LAN multicast group; nothing is mocked. The UPnP/SSDP variant
is marked SKIP because it relies on an ``M-SEARCH`` multicast round-trip that is
unreliable (and frequently blocks) inside sandboxed CI runners.
"""
import time

import pytest

# zeroconf is an optional (LGPL) transport for end users, but the [test] extra
# installs it so this real advertise<->discover suite always runs in CI.
import zeroconf  # noqa: F401

from hivemind_presence.presence import LocalPresence
from hivemind_presence.discovery import LocalDiscovery


def _wait_for_node(discovery, timeout=20):
    """Block until the discovery client sees at least one node, or time out."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if discovery.nodes:
            return True
        time.sleep(0.2)
    return False


def test_zeroconf_advertise_then_discover():
    """A LocalPresence advertises over zeroconf; an independent LocalDiscovery
    finds it and reads back the announced host/port/name."""
    port = 5678
    name = "E2E-Zeroconf-Node"

    presence = LocalPresence(port=port, name=name, upnp=False, zeroconf=True)
    if presence.zero is None:
        pytest.skip("zeroconf transport unavailable in this environment")

    discovery = LocalDiscovery(upnp=False, zeroconf=True)
    found = []
    discovery.on_new_node = lambda node: found.append(node)

    try:
        presence.start()
        discovery.start()
        assert _wait_for_node(discovery), (
            "discovery client never saw the advertised zeroconf node"
        )
    finally:
        discovery.stop()
        presence.stop()

    assert found, "on_new_node callback was never fired"
    node = found[0]
    # the announced connection parameters survived the real mDNS round-trip
    assert node.friendly_name == name
    assert node.port == port
    assert node.host  # a concrete advertised address, not empty
    assert node.address == f"{node.host}:{port}"


def test_zeroconf_service_type_filtering():
    """A discovery client scanning for a different service_type must NOT pick up
    a node advertised under the default HiveMind service_type."""
    presence = LocalPresence(port=5679, name="Typed-Node",
                             service_type="HiveMind-websocket",
                             upnp=False, zeroconf=True)
    if presence.zero is None:
        pytest.skip("zeroconf transport unavailable in this environment")

    discovery = LocalDiscovery(upnp=False, zeroconf=True,
                               service_type="SomeOtherService")
    try:
        presence.start()
        discovery.start()
        # give the exchange ample time; we expect to find NOTHING
        assert not _wait_for_node(discovery, timeout=6), (
            "discovery matched a node under the wrong service_type"
        )
    finally:
        discovery.stop()
        presence.stop()


@pytest.mark.skip(
    reason="UPnP/SSDP discovery needs an M-SEARCH multicast round-trip that is "
           "unreliable and often blocks inside sandboxed CI runners; the zeroconf "
           "path above provides the real advertise<->discover coverage."
)
def test_upnp_advertise_then_discover():
    """Placeholder documenting the intended UPnP/SSDP e2e (see skip reason)."""
    presence = LocalPresence(port=5678, name="E2E-UPnP-Node",
                             upnp=True, zeroconf=False)
    discovery = LocalDiscovery(upnp=True, zeroconf=False)
    try:
        presence.start()
        discovery.start()
        assert _wait_for_node(discovery, timeout=30)
    finally:
        discovery.stop()
        presence.stop()
