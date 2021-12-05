from HiveMind_presence.upnp_server import UPNPAnnounce


class LocalPresence:
    def __init__(self, port=5678, ssl=False,
                 service_type="HiveMind-websocket",
                 name="HiveMind-Node", upnp=True, zeroconf=True):
        self._nodes = {}
        self.upnp = None
        self.zero = None

        if upnp:
            self.upnp = UPNPAnnounce(port=port, ssl=ssl, name=name,
                                     service_type=service_type)
        if zeroconf:
            self._init_zeroconf(port=port, ssl=ssl, name=name,
                                service_type=service_type)
        self.running = False

    def _init_upnp(self, port=5678, ssl=False,
                       service_type="HiveMind-websocket",
                       name="HiveMind-Node"):
        self.upnp = UPNPAnnounce(port=port, ssl=ssl, name=name,
                                 service_type=service_type)

    def _init_zeroconf(self, port=5678, ssl=False,
                       service_type="HiveMind-websocket",
                       name="HiveMind-Node"):
        try:
            from HiveMind_presence.zero import ZeroConfAnnounce
            self.zero = ZeroConfAnnounce(port=port, ssl=ssl, name=name,
                                         service_type=service_type)
        except ImportError:
            # optional dependency, LGPL licensed
            # needs to be installed by user explicitly
            self.zero = None

    def start(self):
        if self.zero:
            self.zero.start()
        self.upnp.start()
        self.running = True

    def stop(self):
        if self.zero:
            self.zero.stop()
        self.upnp.stop()
        self.running = False
