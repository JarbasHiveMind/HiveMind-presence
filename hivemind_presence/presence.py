from hivemind_presence.utils import LOG


class LocalPresence:
    """Announces a HiveMind hub on the local network via HiveBeacon UDP broadcast.

    HiveBeacon requires no external packages and is purpose-built for
    decentralized HiveMind mesh networks. It broadcasts hub information
    every 2 seconds on the local subnet.

    Args:
        port: HiveMind listening port (default: 5678).
        ssl: Whether hub uses SSL (included in broadcast).
        service_type: HiveMind service type tag (default: "HiveMind-websocket").
        name: Human-readable hub name (default: "HiveMind-Node").
    """

    def __init__(self, port=5678, ssl=False,
                 service_type="HiveMind-websocket",
                 name="HiveMind-Node"):
        self._nodes = {}
        self.beacon = None
        self._init_beacon(name=name)
        self.running = False

    def _init_beacon(self, name: str = "HiveMind-Node", site_id: str = "default"):
        from hivemind_presence.beacon import BeaconAnnounce
        self.beacon = BeaconAnnounce(name=name, site_id=site_id)

    def start(self):
        self.beacon.start()
        self.running = True

    def stop(self):
        self.beacon.stop()
        self.running = False
