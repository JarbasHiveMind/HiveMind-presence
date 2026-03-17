"""HiveBeacon UDP broadcast backend — server (announce) and client (scan).

The beacon protocol is a simple UDP broadcast: the hub sends a JSON payload
every ``BROADCAST_INTERVAL`` seconds; listeners parse it and yield
``HiveMindNode`` objects.

No external packages required.
"""
import json
import os
import socket
import threading
import time
from threading import Thread

from hivemind_presence.devices import AbstractDevice, HiveMindNode
from hivemind_presence.utils import LOG

BROADCAST_PORT = 56789
BROADCAST_INTERVAL = 2  # seconds
BUFFER_SIZE = 8192
CONFIG_PATH = os.path.expanduser("~/.config/hivemind-core/server.json")


def _get_local_ip() -> str:
    """Return the primary local IPv4 address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


class BeaconServer(Thread):
    """Broadcasts HiveMind hub info via UDP every ``BROADCAST_INTERVAL`` seconds.

    The config file is re-read on every cycle so changes to ``server.json``
    take effect without restarting the beacon.

    Args:
        device_name: Human-readable name included in each broadcast payload.
        site_id: Site/room identifier included in each broadcast payload.
        config: Path to the server JSON config file (default: ``~/.config/hivemind-core/server.json``).
    """

    def __init__(self, device_name: str = "HiveMind-Node",
                 site_id: str = "default",
                 config: str = None):
        """
                 Initialize the BeaconServer thread with the device identity and configuration path.
                 
                 Parameters:
                     device_name (str): Human-readable name advertised by the beacon (default "HiveMind-Node").
                     site_id (str): Site identifier included in broadcasts (default "default").
                     config (str | None): Path to the server JSON config file; if None, uses the module default CONFIG_PATH.
                 
                 Notes:
                     The instance is created as a daemon thread and an internal stop event is initialized for controlling the broadcast loop.
                 """
                 super().__init__(daemon=True)
        self.device_name = device_name
        self.site_id = site_id
        self._config_path = config or CONFIG_PATH
        self._stop_event = threading.Event()

    def _load_config(self) -> dict:
        """
        Load the server configuration from the configured JSON file.
        
        Returns:
            config (dict): Parsed JSON configuration; returns an empty dict if the file is missing or any error occurs while reading or parsing.
        """
        if os.path.isfile(self._config_path):
            try:
                with open(self._config_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _build_payload(self) -> dict:
        """
        Constructs the hub payload describing this device for UDP broadcast.
        
        Returns:
            payload (dict): Dictionary with keys:
                - "device_name": configured device name.
                - "site_id": configured site identifier.
                - "host": primary local IPv4 address.
                - "capabilities": dict containing "binarize", "encodings" (list), and "ciphers" (list).
                - "agent": agent protocol module name or None.
                - "binary_handler": binary protocol module name or None.
                - "protocols": mapping of protocol name to {"port": int|None, "ssl": bool|None}.
        """
        cfg = self._load_config()

        return {
            "device_name": self.device_name,
            "site_id": self.site_id,
            "host": _get_local_ip(),
            "capabilities": {
                "binarize": cfg.get("binarize"),
                "encodings": cfg.get("allowed_encodings", []),
                "ciphers": cfg.get("allowed_ciphers", []),
            },
            "agent": cfg.get("agent_protocol", {}).get("module"),
            "binary_handler": cfg.get("binary_protocol", {}).get("module"),
            "protocols": {
                p: {"port": k.get("port"), "ssl": k.get("ssl")}
                for p, k in cfg.get("network_protocol", {}).items()
            },
        }

    def stop(self) -> None:
        """Signal the broadcast thread to stop."""
        self._stop_event.set()

    def run(self) -> None:
        """
        Periodically broadcasts the server payload over UDP to the local network until a stop signal is set.
        
        Builds the payload, encodes it as UTF-8 JSON, and sends it to 255.255.255.255 on BROADCAST_PORT at BROADCAST_INTERVAL intervals. Ensures the UDP socket is closed when the loop exits.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            while not self._stop_event.is_set():
                payload = self._build_payload()
                encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                sock.sendto(encoded, ("255.255.255.255", BROADCAST_PORT))
                self._stop_event.wait(BROADCAST_INTERVAL)
        finally:
            sock.close()


class BeaconListener:
    """Listens for ``BeaconServer`` UDP broadcasts and yields raw hub-info dicts.

    Args:
        port: UDP port to listen on (default: ``BROADCAST_PORT``).
    """

    def __init__(self, port: int = BROADCAST_PORT):
        """
        Initialize the BeaconListener.
        
        Parameters:
            port (int): UDP port to bind for receiving beacon broadcasts (defaults to BROADCAST_PORT).
        
        Description:
            Stores the listening port and creates an internal event used to signal stopping the listener loop.
        """
        self.port = port
        self._stop_event = threading.Event()

    def stop(self) -> None:
        """Stop the listener (causes ``listen()`` generator to return)."""
        self._stop_event.set()

    def listen(self, timeout: float = None, deduplicate: bool = True):
        """Generator that yields hub-info dicts received via UDP broadcast.

        Args:
            timeout: Total seconds to listen; ``None`` runs until ``stop()`` called.
            deduplicate: If ``True``, skip repeated payloads from the same host+device_name.

        Yields:
            dict: Raw hub-info payload as broadcast by ``BeaconServer``.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(1.0)
        sock.bind(("", self.port))

        seen: set = set()
        deadline = time.monotonic() + timeout if timeout is not None else None

        try:
            while not self._stop_event.is_set():
                if deadline is not None and time.monotonic() >= deadline:
                    break
                try:
                    data, addr = sock.recvfrom(BUFFER_SIZE)
                except socket.timeout:
                    continue
                try:
                    message = json.loads(data.decode("utf-8"))
                except Exception:
                    continue
                if not message:
                    continue
                if deduplicate:
                    key = (addr[0], message.get("device_name"))
                    if key in seen:
                        continue
                    seen.add(key)
                yield message
        finally:
            sock.close()


class BeaconAnnounce:
    """Announces a HiveMind hub on the local network via UDP broadcast.

    Wraps ``BeaconServer``.  Config is re-read on each broadcast cycle so
    changes to ``server.json`` take effect without restarting.

    Args:
        name: Human-readable device name to include in broadcasts.
        site_id: Site/room identifier to include in broadcasts.
    """

    def __init__(self, name: str = "HiveMind-Node", site_id: str = "default"):
        """
        Create a BeaconAnnounce that wraps an internal BeaconServer for broadcasting.
        
        Parameters:
        	name (str): Human-readable device name to advertise.
        	site_id (str): Identifier for the site/group the device belongs to.
        """
        self._server = BeaconServer(device_name=name, site_id=site_id)

    def start(self) -> None:
        """Start broadcasting."""
        self._server.start()

    def stop(self) -> None:
        """Stop broadcasting."""
        self._server.stop()


class BeaconScanner(Thread):
    """Discovers HiveMind hubs via UDP broadcast.

    Wraps ``BeaconListener`` in a daemon thread.
    Calls ``on_new_node(node: HiveMindNode)`` for each newly discovered hub.

    Args:
        service_type: HiveMind service type tag to attach to discovered nodes.
        timeout: Seconds to scan; ``None`` runs until ``stop()`` is called.
    """

    def __init__(self, service_type: str = "HiveMind-websocket",
                 timeout: float = None):
        """
                 Initialize the BeaconScanner.
                 
                 Parameters:
                     service_type (str): Service type tag to attach to discovered nodes; defaults to "HiveMind-websocket".
                     timeout (float): Optional per-listen timeout in seconds for discovery operations; if None, listening may block indefinitely.
                 
                 Description:
                     Creates an internal BeaconListener, stores scanning configuration, initializes the running flag, and sets
                     `on_new_node` to a no-op callback that will be invoked with each discovered node.
                 """
                 super().__init__(daemon=True)
        self._listener = BeaconListener()
        self._service_type = service_type
        self._timeout = timeout
        self.running = False
        self.on_new_node = lambda node: None

    def stop(self) -> None:
        """Stop the scanner."""
        self.running = False
        self._listener.stop()

    def run(self) -> None:
        """
        Continuously discovers HiveMind hubs via the listener and notifies about each unique node.
        
        Runs until stop() is called or the scanner's timeout elapses. For each received hub payload, constructs a HiveMindNode (using the first listed protocol's port and ssl when present, defaulting to port 5678 and ssl False) and invokes the scanner's on_new_node callback with that node. Duplicate discoveries for the same host:port are suppressed.
        """
        self.running = True
        seen: set = set()
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
