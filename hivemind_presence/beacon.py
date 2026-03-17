"""HiveBeacon UDP broadcast backend for hivemind-presence.

Requires the optional `hivebeacon` package.  Import is deferred to first use
so that hivemind-presence can be imported even when hivebeacon is not installed.
"""
import threading

from hivemind_presence.devices import HiveMindNode, AbstractDevice
from hivemind_presence.utils import LOG


class BeaconAnnounce:
    """Announces a HiveMind hub via HiveBeacon UDP broadcast.

    Wraps ``hivebeacon.BeaconServer``.  The server re-reads
    ``~/.config/hivemind-core/server.json`` on every broadcast cycle, so
    port/ssl info is always current without restarting.
    """

    def __init__(self, name="HiveMind-Node", site_id="default"):
        from hivebeacon import BeaconServer  # optional dep
        self._server = BeaconServer(device_name=name, site_id=site_id)

    def start(self):
        self._server.start()

    def stop(self):
        self._server.stop()


class BeaconScanner(threading.Thread):
    """Discovers HiveMind hubs via HiveBeacon UDP broadcast.

    Wraps ``hivebeacon.BeaconListener`` in a daemon thread.
    Calls ``on_new_node(node: HiveMindNode)`` for each newly discovered hub.
    """

    def __init__(self, service_type="HiveMind-websocket", timeout=None):
        super().__init__(daemon=True)
        from hivebeacon import BeaconListener  # optional dep
        self._listener = BeaconListener()
        self._service_type = service_type
        self._timeout = timeout
        self.running = False
        self.on_new_node = lambda node: None

    def stop(self):
        self.running = False
        self._listener.stop()

    def run(self):
        self.running = True
        seen = set()
        for hub in self._listener.listen(timeout=self._timeout):
            if not self.running:
                break
            host = hub.get("host", "")
            protocols = hub.get("protocols", {})
            port = 5678
            ssl = False
            for _, info in protocols.items():
                port = info.get("port") or port
                ssl = info.get("ssl", False)
                break

            addr = f"{host}:{port}"
            if addr in seen:
                continue
            seen.add(addr)

            device = AbstractDevice(
                host=host,
                port=port,
                ssl=ssl,
                device_type=self._service_type,
                name=hub.get("device_name", "HiveMind-Node"),
            )
            node = HiveMindNode(device)
            LOG.info(f"HiveBeacon node found: {node.address}")
            self.on_new_node(node)
