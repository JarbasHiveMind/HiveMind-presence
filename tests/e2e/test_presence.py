"""E2E tests for HiveMind presence tracking."""

from hivescope import TopologyBuilder
from hivescope.scenarios import three_satellites
from hivescope.assertions import assert_client_registered


def test_presence_tracked_on_connection():
    """Master tracks satellite presence on connection."""
    b = three_satellites()
    try:
        b.start_all()
        m = b.get_master("M0")
        connected = m.connected_peers()
        assert len(connected) == 3, "Expected 3 satellites connected"
    finally:
        b.stop_all()


def test_multiple_satellites_presence():
    """Multiple satellites' presence is tracked."""
    b = three_satellites()
    try:
        b.start_all()
        m = b.get_master("M0")
        for i in range(3):
            s = b.get_satellite(f"S{i}")
            assert_client_registered(m, s.peer)
    finally:
        b.stop_all()
