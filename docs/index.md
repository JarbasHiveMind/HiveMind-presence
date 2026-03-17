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
pip install -e HiveMind-presence/
```
