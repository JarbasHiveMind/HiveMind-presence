# Local Discovery Implementation

The `LocalDiscovery` class is used by HiveMind satellites to scan the local network for available HiveMind hubs.

- **Source File**: `HiveMind-presence/hivemind_presence/discovery.py`
- **Primary Class**: `LocalDiscovery`

## Backend Initialization

Similar to `LocalPresence`, the `LocalDiscovery` class initializes its scanners only if the dependencies are present.

- **UPnP**: `_init_upnp()` (uses `hivemind_presence.upnp_server.UPNPScanner`)
- **Zeroconf**: `_init_zeroconf()` (uses `hivemind_presence.zero.ZeroScanner`)
- **Beacon**: `_init_beacon()` (uses `hivemind_presence.beacon.BeaconScanner`)
- **GGWave**: `_init_ggwave()` (uses `hivemind_presence.ggwave.GGWaveScanner`)

## Core Methods

### 1. `scan(timeout=25)`
This is a generator that starts all scanners and yields unique `HiveMindNode` objects as they are discovered.
- **Deduplication**: It maintains a `seen` list of node addresses to ensure each hub is only reported once.
- **Source**: `LocalDiscovery.scan(timeout)`

### 2. `on_new_node(node)`
This callback is triggered whenever any backend finds a new device. It wraps the raw discovery data into a `HiveMindNode` object and stores it in `self._nodes`.
- **Source**: `LocalDiscovery.on_new_node(node)`

## Discovered Node Data
The resulting `HiveMindNode` (defined in `hivemind_presence.devices`) provides access to:
- `node.host`: IP address of the hub.
- `node.port`: Listening port.
- `node.ssl`: Boolean indicating if SSL is required.
- `node.address`: A formatted URL string (e.g., `ws://192.168.1.10:5678`).
