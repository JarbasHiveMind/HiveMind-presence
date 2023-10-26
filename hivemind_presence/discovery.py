import time

from hivemind_presence.upnp_server import UPNPScanner
from hivemind_presence.utils import LOG
from hivemind_presence.devices import HiveMindNode, AbstractDevice


class LocalDiscovery:
    def __init__(self, zeroconf=True, upnp=True, service_type="HiveMind-websocket"):
        self._nodes = {}
        self.zero = None
        self.upnp = None
        self.service_type = service_type
        if upnp:
            self.upnp = UPNPScanner(identifier=self.service_type)
            self.upnp.on_new_node = self.on_new_upnp_node
        if zeroconf:
            self._init_zeroconf()
        self.running = False
        if not zeroconf and not upnp:
            raise ValueError("at least one of zeroconf or upnp must be enabled")

    def _init_zeroconf(self):
        try:
            from hivemind_presence.zero import ZeroScanner
            self.zero = ZeroScanner(identifier=self.service_type)
            self.zero.on_new_node = self.on_new_zeroconf_node
        except ImportError:
            # optional dependency, LGPL licensed
            # needs to be installed by user explicitly
            self.zero = None

    def on_new_zeroconf_node(self, node):
        d = AbstractDevice(host=node["host"], port=node["port"],
                       device_type=self.service_type,
                       name=node["name"])
        node = HiveMindNode(d)
        LOG.info("ZeroConf Node Found: " + str(node.address))
        self._nodes[node.address] = node
        self.on_new_node(node)

    def on_new_upnp_node(self, node):
        LOG.info("UpNp Node Found: " + node.address)
        self._nodes[node.address] = node
        self.on_new_node(node)

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
        self.running = False
