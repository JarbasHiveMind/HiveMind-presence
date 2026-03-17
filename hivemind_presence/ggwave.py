"""GGWave audio pairing backend for hivemind-presence.

Requires the optional ``hivemind-ggwave`` package and the ``ggwave-rx``/
``ggwave-cli`` binaries.  Import is deferred to first use.

On the hub side (``GGWaveAnnounce``) this wraps ``GGWaveMaster``.
On the satellite side (``GGWaveScanner``) this wraps ``GGWaveSlave`` and
converts the resulting ``NodeIdentity`` into a ``HiveMindNode`` so callers
receive the same type as all other discovery backends.
"""
from hivemind_presence.utils import LOG


class GGWaveAnnounce:
    """Hub-side audio pairing.  Wraps ``GGWaveMaster``.

    Args:
        pswd: Pairing password (auto-generated if None).
        host: Hub IP to broadcast (auto-detected if None).
        silent_mode: If True, the password is not broadcast over audio.
        config: Forwarded to ``GGWave``.
        add_client_callback: Called with ``(access_key, pswd)`` instead of
            importing ``hivemind_core.ClientDatabase``.  Must be provided
            unless hivemind-core is installed.
    """

    def __init__(self, pswd=None, host=None, silent_mode=False,
                 config=None, add_client_callback=None):
        from hivemind_ggwave import GGWaveMaster  # optional dep
        self._master = GGWaveMaster(
            pswd=pswd,
            host=host,
            silent_mode=silent_mode,
            config=config,
            add_client_callback=add_client_callback,
        )

    def start(self):
        self._master.start()

    def stop(self):
        self._master.stop()


class GGWaveScanner:
    """Satellite-side audio pairing.  Wraps ``GGWaveSlave``.

    Listens for ``hm.ggwave.identity_updated`` on the internal FakeBus,
    reads the saved ``NodeIdentity``, and calls ``on_new_node(HiveMindNode)``
    so the caller can treat it identically to UPnP/Zeroconf/Beacon discoveries.
    """

    def __init__(self, config=None):
        from hivemind_ggwave import GGWaveSlave  # optional dep
        from ovos_utils.fakebus import FakeBus
        self._bus = FakeBus()
        self._slave = GGWaveSlave(bus=self._bus, config=config)
        self.on_new_node = lambda node: None
        self._setup_listener()

    def _setup_listener(self):
        from hivemind_bus_client.identity import NodeIdentity
        from hivemind_presence.devices import HiveMindNode, AbstractDevice

        def on_identity_updated(message=None):
            identity = NodeIdentity()
            master = identity.default_master or ""
            ssl = master.startswith("wss://")
            for prefix in ("wss://", "ws://", "https://", "http://"):
                if master.startswith(prefix):
                    master = master[len(prefix):]
                    break
            if ":" in master:
                host, port_str = master.rsplit(":", 1)
                try:
                    port = int(port_str)
                except ValueError:
                    host = master
                    port = identity.default_port or 5678
            else:
                host = master
                port = identity.default_port or 5678

            if not host:
                return

            device = AbstractDevice(
                host=host,
                port=port,
                ssl=ssl,
                device_type="HiveMind-websocket",
                name="HiveMind-Node",
            )
            node = HiveMindNode(device)
            LOG.info(f"GGWave pairing: discovered hub at {node.address}")
            self.on_new_node(node)

        self._bus.on("hm.ggwave.identity_updated", on_identity_updated)

    def start(self):
        self._slave.start()

    def stop(self):
        self._slave.stop()
