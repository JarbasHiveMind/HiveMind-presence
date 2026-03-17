# HiveMind Presence

HiveMind Presence is a unified discovery and announcement framework for the HiveMind ecosystem. It supports multiple backends (Zeroconf, UPnP, and HiveBeacon) to allow Minds to announce themselves and satellites to find them.

## Documentation Guides

- [Local Presence](presence.md) - How a Mind announces itself.
- [Local Discovery](discovery.md) - How a Satellite finds a Mind.

## Overview

The library provides a high-level API that abstracts away the complexity of various network discovery protocols. It is modular, meaning backends are only activated if their required dependencies are installed.

## Backends

| Backend | Protocol | Package Dependency |
|---|---|---|
| **Zeroconf** | mDNS/DNS-SD | `zeroconf` |
| **UPnP** | SSDP | `upnpclient` |
| **Beacon** | UDP Broadcast | `hivebeacon` |

## Installation

```bash
pip install -e HiveMind-presence/
```
