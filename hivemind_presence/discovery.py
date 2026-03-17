import time

from hivemind_presence.utils import LOG
from hivemind_presence.devices import HiveMindNode, AbstractDevice


class LocalDiscovery:
    """Scans the local network for HiveMind hubs.

    Each protocol backend is **independently optional** and controlled by a
    boolean flag.  Missing optional packages are silently skipped.

    Backends:
        upnp     – UPnP/SSDP (requires ``upnpclient``; installed with package)
        zeroconf – mDNS/Zeroconf (requires optional ``zeroconf`` package)
        beacon   – HiveBeacon UDP broadcast (requires optional ``hivebeacon``)
        ggwave   – Audio credential pairing (requires optional
                   ``hivemind-ggwave`` + ggwave binaries)

    Raises:
        ValueError: If all backends are disabled.
    """

    def __init__(self, zeroconf=True, upnp=True, beacon=True, ggwave=False,
                 service_type="HiveMind-websocket"):
        self._nodes = {}
        self.zero = None
        self.upnp = None
        self.beacon = None
        self.ggwave_scanner = None
        self.service_type = service_type

        if upnp:
            self._init_upnp()
        if zeroconf:
            self._init_zeroconf()
        if beacon:
            self._init_beacon()
        if ggwave:
            self._init_ggwave()

        self.running = False

        if not any([self.zero, self.upnp, self.beacon, self.ggwave_scanner]):
            raise ValueError(
                "No discovery backends available. Enable at least one of: "
                "upnp, zeroconf, beacon, ggwave — and ensure the required "
                "packages are installed."
            )

    def _init_upnp(self):
        try:
            from hivemind_presence.upnp_server import UPNPScanner
            self.upnp = UPNPScanner(identifier=self.service_type)
            self.upnp.on_new_node = self.on_new_upnp_node
        except ImportError:
            LOG.debug("upnpclient not installed; UPnP scan disabled")
            self.upnp = None

    def _init_zeroconf(self):
        try:
            from hivemind_presence.zero import ZeroScanner
            self.zero = ZeroScanner(identifier=self.service_type)
            self.zero.on_new_node = self.on_new_zeroconf_node
        except ImportError:
            # optional dependency, LGPL licensed
            # needs to be installed by user explicitly
            self.zero = None

    def _init_beacon(self):
        try:
            from hivemind_presence.beacon import BeaconScanner
            self.beacon = BeaconScanner(service_type=self.service_type)
            self.beacon.on_new_node = self.on_new_beacon_node
        except ImportError:
            LOG.debug("hivebeacon not installed; HiveBeacon UDP scan disabled")
            self.beacon = None

    def _init_ggwave(self):
        try:
            from hivemind_presence.ggwave import GGWaveScanner
            self.ggwave_scanner = GGWaveScanner()
            self.ggwave_scanner.on_new_node = self.on_new_ggwave_node
        except (ImportError, ValueError) as e:
            LOG.debug(f"GGWave scanner unavailable: {e}")
            self.ggwave_scanner = None

    # ---------- per-backend callbacks ----------

    def on_new_zeroconf_node(self, node):
        d = AbstractDevice(host=node["host"], port=node["port"],
                           device_type=self.service_type,
                           name=node["name"])
        node = HiveMindNode(d)
        LOG.info("ZeroConf Node Found: " + str(node.address))
        self._nodes[node.address] = node
        self.on_new_node(node)

    def on_new_upnp_node(self, node):
        LOG.info("UPnP Node Found: " + node.address)
        self._nodes[node.address] = node
        self.on_new_node(node)

    def on_new_beacon_node(self, node):
        LOG.info("HiveBeacon Node Found: " + node.address)
        self._nodes[node.address] = node
        self.on_new_node(node)

    def on_new_ggwave_node(self, node):
        LOG.info("GGWave Node Found: " + node.address)
        self._nodes[node.address] = node
        self.on_new_node(node)

    # ---------- public API ----------

    def on_new_node(self, node):
        LOG.debug("Node Data: " + str(node.data))

    @property
    def nodes(self):
        return self._nodes

    def start(self):
        if self.zero:
            self.zero.start()
        if self.upnp:
            self.upnp.start()
        if self.beacon:
            self.beacon.start()
        if self.ggwave_scanner:
            self.ggwave_scanner.start()
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
        if self.zero:
            self.zero.stop()
        if self.upnp:
            self.upnp.stop()
        if self.beacon:
            self.beacon.stop()
        if self.ggwave_scanner:
            self.ggwave_scanner.stop()
        self.running = False
