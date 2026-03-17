from hivemind_presence.utils import LOG


class LocalPresence:
    """Announces a HiveMind hub on the local network.

    Each protocol backend is **independently optional** and controlled by a
    boolean flag.  Missing optional packages are silently skipped.

    Backends:
        upnp     – UPnP/SSDP (requires ``upnpclient``; installed with package)
        zeroconf – mDNS/Zeroconf (requires optional ``zeroconf`` package)
        beacon   – HiveBeacon UDP broadcast (built-in; no extra packages needed)
        ggwave   – Audio pairing / GGWaveMaster (requires optional
                   ``hivemind-ggwave`` + ggwave binaries)

    Args:
        ggwave_add_client_callback: Required when ``ggwave=True``; called with
            ``(access_key: str, pswd: str)`` to register a pairing request
            without importing hivemind-core directly.
    """

    def __init__(self, port=5678, ssl=False,
                 service_type="HiveMind-websocket",
                 name="HiveMind-Node",
                 upnp=True, zeroconf=True, beacon=True, ggwave=False,
                 ggwave_pswd=None, ggwave_host=None, ggwave_silent=False,
                 ggwave_add_client_callback=None):
        self._nodes = {}
        self.upnp = None
        self.zero = None
        self.beacon = None
        self.ggwave_announce = None

        if upnp:
            self._init_upnp(port=port, ssl=ssl, name=name,
                            service_type=service_type)
        if zeroconf:
            self._init_zeroconf(port=port, ssl=ssl, name=name,
                                service_type=service_type)
        if beacon:
            self._init_beacon(name=name)
        if ggwave:
            self._init_ggwave(pswd=ggwave_pswd, host=ggwave_host,
                              silent_mode=ggwave_silent,
                              add_client_callback=ggwave_add_client_callback)

        self.running = False

    def _init_upnp(self, port=5678, ssl=False,
                   service_type="HiveMind-websocket",
                   name="HiveMind-Node"):
        try:
            from hivemind_presence.upnp_server import UPNPAnnounce
            self.upnp = UPNPAnnounce(port=port, ssl=ssl, name=name,
                                     service_type=service_type)
        except ImportError:
            LOG.debug("upnpclient not installed; UPnP announce disabled")
            self.upnp = None

    def _init_zeroconf(self, port=5678, ssl=False,
                       service_type="HiveMind-websocket",
                       name="HiveMind-Node"):
        try:
            from hivemind_presence.zero import ZeroConfAnnounce
            self.zero = ZeroConfAnnounce(port=port, ssl=ssl, name=name,
                                         service_type=service_type)
        except ImportError:
            # optional dependency, LGPL licensed
            # needs to be installed by user explicitly
            self.zero = None

    def _init_beacon(self, name: str = "HiveMind-Node", site_id: str = "default"):
        from hivemind_presence.beacon import BeaconAnnounce
        self.beacon = BeaconAnnounce(name=name, site_id=site_id)

    def _init_ggwave(self, pswd=None, host=None, silent_mode=False,
                     add_client_callback=None):
        try:
            from hivemind_presence.ggwave import GGWaveAnnounce
            self.ggwave_announce = GGWaveAnnounce(
                pswd=pswd,
                host=host,
                silent_mode=silent_mode,
                add_client_callback=add_client_callback,
            )
        except (ImportError, ValueError) as e:
            LOG.debug(f"GGWave announce unavailable: {e}")
            self.ggwave_announce = None

    def start(self):
        if self.zero:
            self.zero.start()
        if self.upnp:
            self.upnp.start()
        if self.beacon:
            self.beacon.start()
        if self.ggwave_announce:
            self.ggwave_announce.start()
        self.running = True

    def stop(self):
        if self.zero:
            self.zero.stop()
        if self.upnp:
            self.upnp.stop()
        if self.beacon:
            self.beacon.stop()
        if self.ggwave_announce:
            self.ggwave_announce.stop()
        self.running = False
