# Local Presence Implementation

The `LocalPresence` class is used by a HiveMind Mind to announce its services on the local network using all available backends.

- **Source File**: `HiveMind-presence/hivemind_presence/presence.py`
- **Primary Class**: `LocalPresence`

## Backend Initialization

The constructor (`__init__`) checks the provided boolean flags and attempts to initialize each requested backend. If a required dependency is missing, it logs a debug message and disables that backend.

- **UPnP**: `_init_upnp()` (uses `hivemind_presence.upnp_server.UPNPAnnounce`)
- **Zeroconf**: `_init_zeroconf()` (uses `hivemind_presence.zero.ZeroConfAnnounce`)
- **Beacon**: `_init_beacon()` (uses `hivemind_presence.beacon.BeaconAnnounce`)

## Core Methods

### 1. `start()`
Starts all initialized backends. For example, `self.zero.start()` begins broadcasting the mDNS record.
- **Source**: `LocalPresence.start()`

### 2. `stop()`
Gracefully shuts down all active backends and stops announcements.
- **Source**: `LocalPresence.stop()`

## Usage in `hivemind-core`
The `hivemind-core` service uses `LocalPresence` to ensure that new satellites can find it without manual configuration.
