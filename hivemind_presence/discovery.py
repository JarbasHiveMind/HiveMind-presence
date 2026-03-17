import time

from hivemind_presence.utils import LOG
from hivemind_presence.devices import HiveMindNode, AbstractDevice


class LocalDiscovery:
    """Scans the local network for HiveMind hubs via HiveBeacon UDP broadcast.

    HiveBeacon requires no external packages and is purpose-built for
    decentralized HiveMind mesh networks. It broadcasts hub information
    every 2 seconds on the local subnet.

    Args:
        service_type: HiveMind service type tag to attach to discovered nodes.
    """

    def __init__(self, service_type="HiveMind-websocket"):
        self._nodes = {}
        self.beacon = None
        self.service_type = service_type
        self._init_beacon()
        self.running = False

    def _init_beacon(self):
        from hivemind_presence.beacon import BeaconScanner
        self.beacon = BeaconScanner(service_type=self.service_type)
        self.beacon.on_new_node = self.on_new_beacon_node

    # ---------- backend callback ----------

    def on_new_beacon_node(self, node):
        LOG.info("HiveBeacon Node Found: " + node.address)
        self._nodes[node.address] = node
        self.on_new_node(node)

    # ---------- public API ----------

    def on_new_node(self, node):
        LOG.debug("Node Data: " + str(node.data))

    @property
    def nodes(self):
        return self._nodes

    def start(self):
        self.beacon.start()
        self.running = True

    def scan(self, timeout=25):
        if not self.running:
            self.start()
        seen = []
        start = time.time()
        while time.time() - start <= timeout:
            for node in self._nodes.values():
                if node.address not in seen:
                    seen.append(node.address)
                    yield node
            time.sleep(0.1)

    def stop(self):
        self.beacon.stop()
        self.running = False
