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
        """
        Initialize a LocalDiscovery instance configured for the given HiveMind beacon service type.
        
        Parameters:
            service_type (str): Service type tag used to filter/identify HiveMind beacon broadcasts (default "HiveMind-websocket").
        
        Attributes set:
            _nodes (dict): Local cache mapping node addresses to node objects.
            beacon: Beacon scanner instance initialized for the given service_type.
            running (bool): Discovery running state, initialized to False.
        """
        self._nodes = {}
        self.beacon = None
        self.service_type = service_type
        self._init_beacon()
        self.running = False

    def _init_beacon(self):
        """
        Initialize the BeaconScanner for this LocalDiscovery and attach the instance's new-node handler.
        
        This creates a BeaconScanner configured with the instance's service_type and assigns its on_new_node callback to the LocalDiscovery.on_new_beacon_node method, storing the scanner on self.beacon.
        """
        from hivemind_presence.beacon import BeaconScanner
        self.beacon = BeaconScanner(service_type=self.service_type)
        self.beacon.on_new_node = self.on_new_beacon_node

    # ---------- backend callback ----------

    def on_new_beacon_node(self, node):
        """
        Handle a newly discovered HiveBeacon node.
        
        Stores the node in the instance cache keyed by node.address and forwards it to on_new_node for further processing.
        
        Parameters:
            node: An object representing the discovered beacon node. Must have an `address` attribute used as the cache key.
        """
        LOG.info("HiveBeacon Node Found: " + node.address)
        self._nodes[node.address] = node
        self.on_new_node(node)

    # ---------- public API ----------

    def on_new_node(self, node):
        """
        Handle a newly discovered beacon node.
        
        Logs the node's data and provides a hook for subclasses to implement additional processing.
        
        Parameters:
            node: An object representing the discovered node; expected to expose at least `address` and `data` attributes.
        """
        LOG.debug("Node Data: " + str(node.data))

    @property
    def nodes(self):
        """
        Return the internal mapping of discovered HiveMind nodes keyed by their network address.
        
        Returns:
            dict: Mapping from node address (string) to the node object stored in the discovery cache.
        """
        return self._nodes

    def start(self):
        """
        Start the local HiveBeacon discovery scanner.
        
        Invokes the configured BeaconScanner to begin scanning for HiveMind hubs and sets the discovery's running state to True.
        """
        self.beacon.start()
        self.running = True

    def scan(self, timeout=25):
        """
        Yield unique discovered nodes detected within the given time window.
        
        Parameters:
            timeout (int|float): Maximum number of seconds to run the scan.
        
        Returns:
            generator: Yields each discovered node object once, in order of first observation.
        """
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
        """
        Stop active local discovery of HiveMind hubs.
        
        Stops the underlying BeaconScanner and marks the discovery service as not running.
        """
        self.beacon.stop()
        self.running = False
