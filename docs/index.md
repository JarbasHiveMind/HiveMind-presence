# HiveMind Presence

HiveMind Presence is a lightweight discovery and announcement framework for the HiveMind ecosystem. It uses **HiveBeacon** — a simple UDP broadcast protocol — to allow Minds to announce themselves and satellites to discover them on the local network.

## Documentation Guides

- [Local Presence](presence.md) - How a Mind announces itself.
- [Local Discovery](discovery.md) - How a Satellite finds a Mind.

## HiveBeacon Protocol

- **Zero dependencies** — no external packages required
- **Simple UDP broadcast** — sends hub information every 2 seconds on the local subnet
- **Purpose-built for HiveMind** — includes hub config, capabilities, and network metadata
- **Designed for mesh networks** — lightweight and efficient for decentralized deployments

## Installation

```bash
pip install HiveMind-presence
```

Or from source:

```bash
git clone https://github.com/JarbasHiveMind/HiveMind-presence
cd HiveMind-presence
pip install -e .
```

## Quick Example

**Hub side — announce on the network:**

```python
from hivemind_presence import LocalPresence

presence = LocalPresence(name="My Hub", port=5678)
presence.start()
# Broadcasts every 2 seconds, Ctrl+C to stop
```

**Satellite side — discover nearby hubs:**

```python
from hivemind_presence import LocalDiscovery

discovery = LocalDiscovery()

# Scan for up to 30 seconds, print each hub found
for hub in discovery.scan(timeout=30):
    print(f"Found hub: {hub.friendly_name} at {hub.address}")

discovery.stop()
```

See [docs/api.md](api.md) for complete API reference.
