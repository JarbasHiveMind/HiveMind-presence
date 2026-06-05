# HiveMind-presence

Local-network presence and discovery for [HiveMind](https://github.com/JarbasHiveMind/HiveMind-core)
nodes. A node **announces** itself on the LAN so satellites can find the hub
without being told its IP address, and a satellite **scans** the LAN to discover
reachable hubs.

It sits next to [hivemind-core](https://github.com/JarbasHiveMind/HiveMind-core)
(the hub) and the client libraries: the hub advertises its WebSocket address with
`hivemind-presence announce`, and a client uses `hivemind-presence scan` (or the
`LocalDiscovery` API) to locate it and open a connection.

## Discovery transports

- **mDNS / Zeroconf** — multicast DNS service discovery. Optional dependency
  (`zeroconf` is LGPL and imported lazily); install it to enable mDNS.
- **UPnP / SSDP** — an SSDP server advertises a UPnP device descriptor; the
  scanner discovers it over SSDP.

The roadmap moves the default to **HiveBeacon** — a zero-dependency UDP broadcast
beacon absorbed from the archived `HiveBeacon` project — with mDNS kept as an
optional transport. UPnP is being retired. Until the beacon transport ships, mDNS
and UPnP are the available transports.

## Prerequisites

- Python 3.10+
- A HiveMind hub (`hivemind-core`) reachable on the LAN for `scan` to find
  anything.
- For mDNS: the optional `zeroconf` package (`pip install zeroconf`). Without it,
  announce/scan silently fall back to UPnP only.

## Install

```bash
pip install hivemind-presence
```

From source:

```bash
git clone https://github.com/JarbasHiveMind/HiveMind-presence
cd HiveMind-presence
pip install -e .
```

To include mDNS support:

```bash
pip install hivemind-presence zeroconf
```

## Quickstart

On the **hub** (advertise the node):

```bash
hivemind-presence announce --port 5678 --name living_room
```

On a **satellite** (discover hubs on the LAN):

```bash
hivemind-presence scan
```

```
            HiveMind Nodes
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━┓
┃ Friendly Name ┃ Host         ┃ Port ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━┩
│   living_room │ 192.168.1.9  │ 5678 │
│       kitchen │ 192.168.1.13 │ 5678 │
└───────────────┴──────────────┴──────┘
```

Both `announce` and `scan` use mDNS by default (`--zeroconf true --upnp false`).
Pass `--upnp true` to add the UPnP/SSDP transport.

## Programmatic use

Announce from a hub process:

```python
from hivemind_presence import LocalPresence

presence = LocalPresence(port=5678, name="living_room")
presence.start()
# ... run your hub ...
presence.stop()
```

Discover and connect from a client:

```python
from hivemind_presence import LocalDiscovery

disc = LocalDiscovery()
for node in disc.scan(timeout=25):
    bus = node.connect(key="my-access-key", crypto_key="my-crypto-key")
    break
```

`HiveMindNode.connect()` returns a running `HiveMessageBusClient` connected to the
discovered hub.

## Configuration

`announce` and `scan` options:

| Option | Default | Description |
| --- | --- | --- |
| `--port` | `5678` | HiveMind WebSocket port to advertise (announce only). |
| `--name` | `HiveMind-Node` | Friendly device name (announce only). |
| `--service-type` | `HiveMind-websocket` | Service identifier matched between announce and scan. |
| `--zeroconf` | `true` | Use the mDNS/Zeroconf transport. |
| `--upnp` | `false` | Use the UPnP/SSDP transport. |
| `--ssl` | `false` | Advertise SSL support (announce only). |

At least one transport must be enabled for `scan`; `LocalDiscovery` raises if both
are disabled.

## Documentation

See [`docs/`](docs/index.md):

- [How it works](docs/how-it-works.md) — announce/scan flow and the transports.
- [Configuration reference](docs/configuration.md) — every CLI option and API
  argument.
- [Examples](docs/examples.md) — discover-then-connect, hub announce loop.

## License

MIT
