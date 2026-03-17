from hivemind_presence.utils import LOG


class LocalPresence:
    """Announces a HiveMind hub on the local network via HiveBeacon UDP broadcast.

    HiveBeacon requires no external packages and is purpose-built for
    decentralized HiveMind mesh networks. It broadcasts hub information
    every 2 seconds on the local subnet.

    Args:
        port: HiveMind listening port (default: 5678).
        ssl: Whether hub uses SSL (included in broadcast).
        service_type: HiveMind service type tag (default: "HiveMind-websocket").
        name: Human-readable hub name (default: "HiveMind-Node").
    """

    def __init__(self, port=5678, ssl=False,
                 service_type="HiveMind-websocket",
                 name="HiveMind-Node"):
        """
                 Initialize the LocalPresence instance and prepare a HiveBeacon-based beacon for local network announcements.
                 
                 Parameters:
                     port (int): TCP port number of the advertised service (default 5678).
                     ssl (bool): Whether the advertised service uses TLS; influences advertised scheme (default False).
                     service_type (str): Service type identifier used for discovery (default "HiveMind-websocket").
                     name (str): Human-readable node name published by the beacon (default "HiveMind-Node").
                 
                 Notes:
                     Initializes internal node registry, creates and assigns the BeaconAnnounce instance, and sets the running flag to False.
                 """
                 self._nodes = {}
        self.beacon = None
        self._init_beacon(name=name)
        self.running = False

    def _init_beacon(self, name: str = "HiveMind-Node", site_id: str = "default"):
        """
        Initialize and attach a BeaconAnnounce instance used to broadcast this hub on the local network.
        
        Parameters:
            name (str): Service name to advertise over the beacon.
            site_id (str): Identifier for the site or hub group included in beacon announcements.
        """
        from hivemind_presence.beacon import BeaconAnnounce
        self.beacon = BeaconAnnounce(name=name, site_id=site_id)

    def start(self):
        """
        Begin broadcasting the local HiveMind beacon.
        
        Starts the configured BeaconAnnounce instance and sets the instance's running flag to True.
        """
        self.beacon.start()
        self.running = True

    def stop(self):
        """
        Stop announcing this node on the local network.
        
        Stops the beacon's broadcast and updates the instance state to indicate broadcasting is not running.
        """
        self.beacon.stop()
        self.running = False
