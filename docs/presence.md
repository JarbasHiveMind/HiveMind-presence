# Local Presence Implementation

The `LocalPresence` class is used by a HiveMind Mind to announce its services on the local network via HiveBeacon UDP broadcast.

- **Source File**: `HiveMind-presence/hivemind_presence/presence.py`
- **Primary Class**: `LocalPresence`

## HiveBeacon Announcer

The `LocalPresence` class uses a single HiveBeacon announcer with no external dependencies:

- **BeaconAnnounce**: `_init_beacon()` (uses `hivemind_presence.beacon.BeaconAnnounce`)
  - Broadcasts on UDP port 56789 every 2 seconds
  - Re-reads `server.json` on each cycle (changes take effect without restart)
  - Includes hub capabilities, network protocols, and configuration metadata

## Core Methods

### 1. `start()`
Starts all initialized backends. For example, `self.zero.start()` begins broadcasting the mDNS record.
- **Source**: `LocalPresence.start()`

### 2. `stop()`
Gracefully shuts down all active backends and stops announcements.
- **Source**: `LocalPresence.stop()`

## Usage in `hivemind-core`
The `hivemind-core` service uses `LocalPresence` to ensure that new satellites can find it without manual configuration.
