"""Presence cleanup on disconnect."""

from hivescope.scenarios import three_satellites


def test_presence_cleared_after_disconnect():
    b = three_satellites()
    b.start_all()
    try:
        m = b.get_master("M0")
        assert len(m.connected_peers()) == 3

        b.get_satellite("S0").disconnect()
        b.get_satellite("S1").disconnect()
        peers = m.connected_peers()
        assert len(peers) == 1, peers
        assert b.get_satellite("S2").peer in peers
    finally:
        b.stop_all()


def test_all_disconnect_clears_master():
    b = three_satellites()
    b.start_all()
    try:
        m = b.get_master("M0")
        for i in range(3):
            b.get_satellite(f"S{i}").disconnect()
        assert m.connected_peers() == []
    finally:
        b.stop_all()
