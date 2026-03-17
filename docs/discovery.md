# Local Discovery Implementation

The `LocalDiscovery` class is used by HiveMind satellites to scan the local network for available HiveMind hubs via HiveBeacon UDP broadcast.

- **Source File**: `HiveMind-presence/hivemind_presence/discovery.py`
- **Primary Class**: `LocalDiscovery`

## HiveBeacon Scanner

The `LocalDiscovery` class uses a single HiveBeacon scanner with no external dependencies:

- **BeaconScanner**: `_init_beacon()` (uses `hivemind_presence.beacon.BeaconScanner`)
  - Listens on UDP port 56789 for hub broadcasts
  - Deduplicates by host + device name
  - Converts raw beacon payloads to `HiveMindNode` objects

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
