import time

from HiveMind_presence.upnp_server import UPNPScanner
from HiveMind_presence.utils import LOG


class LocalDiscovery:
    def __init__(self):
        self._nodes = {}
        self.upnp = UPNPScanner()
        self.upnp.on_new_node = self.on_new_upnp_node
        self._init_zeroconf()
        self.running = False

    def _init_zeroconf(self):
        try:
            from HiveMind_presence.zero import ZeroScanner
            self.zero = ZeroScanner()
            self.zero.on_new_node = self.on_new_zeroconf_node
        except ImportError:
            # optional dependency, LGPL licensed
            # needs to be installed by user explicitly
            self.zero = None

    def on_new_zeroconf_node(self, node):
        LOG.info("ZeroConf Node Found: " + str(node.address))
        self._nodes[node.address] = node
        self.on_new_node(node)

    def on_new_upnp_node(self, node):
        LOG.info("UpNp Node Found: " + node.address)
        self._nodes[node.address] = node
        self.on_new_node(node)

    def on_new_node(self, node):
        pass

    @property
    def nodes(self):
        return self._nodes

    def start(self):
        if self.zero:
            self.zero.start()
        self.upnp.start()
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
        self.upnp.stop()
        self.running = False
