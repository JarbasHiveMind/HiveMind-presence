# API Reference — HiveMind-presence

Source: `hivemind_presence/`

---

## `LocalPresence`

```python
from hivemind_presence import LocalPresence
```

Announces a HiveMind hub on the local network via HiveBeacon UDP broadcast.

### Constructor

```python
LocalPresence(port=5678, name="HiveMind-Node", service_type="HiveMind-websocket", ssl=False)
```

| Parameter | Type | Description |
|---|---|---|
| `port` | `int` | HiveMind server port to advertise (default: 5678) |
| `name` | `str` | Device friendly name (default: `HiveMind-Node`) |
| `service_type` | `str` | Service identifier tag (default: `HiveMind-websocket`) |
| `ssl` | `bool` | Advertise the port as SSL-enabled (default: `False`) |

### Methods

#### `start()`

Starts HiveBeacon broadcasts. Sends hub information every 2 seconds on UDP port 56789 (multicast address 255.255.255.255).

#### `stop()`

Stops HiveBeacon broadcasts and shuts down background threads cleanly.

---

## `LocalDiscovery`

```python
from hivemind_presence import LocalDiscovery
```

Scans the local network for HiveMind hubs announced via HiveBeacon UDP broadcast.

### Constructor

```python
LocalDiscovery(service_type="HiveMind-websocket")
```

| Parameter | Type | Description |
|---|---|---|
| `service_type` | `str` | Service type filter — only nodes matching this type are reported (default: `HiveMind-websocket`) |

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `nodes` | `dict[str, HiveMindNode]` | All discovered nodes keyed by `"host:port"` |
| `running` | `bool` | Whether discovery is currently active |

### Methods

#### `start()`

Starts the HiveBeacon listener on UDP port 56789 in a background thread.

#### `scan(timeout=25) -> Generator[HiveMindNode, None, None]`

Starts discovery (if not already running) and yields `HiveMindNode` objects as
they are discovered, for up to `timeout` seconds. Yields each node once per
scan call. Polls every 100 ms.

```python
disc = LocalDiscovery()
for node in disc.scan(timeout=15):
    print(node.address)
    disc.stop()
    break
```

#### `stop()`

Stops all background scanning threads.

#### `on_new_node(node: HiveMindNode)`

Callback hook. Called once per newly discovered node. Override or replace to
receive event-driven notifications:

```python
disc = LocalDiscovery()
disc.on_new_node = lambda node: print("found:", node.address)
disc.start()
```

---

## `HiveMindNode`

```python
from hivemind_presence import HiveMindNode
```

Wrapper around a discovered HiveMind hub.

### Properties

| Property | Type | Description |
|---|---|---|
| `friendly_name` | `str` | Human-readable device name |
| `address` | `str` | `"host:port"` string |
| `host` | `str` | IP address |
| `port` | `int` | Port number |
| `ssl` | `bool` | Whether the port uses SSL |
| `device_type` | `str` | Service type identifier |

### Methods

#### `connect(key, crypto_key=None, self_signed=True, useragent="HiveMind-websocket-client") -> HiveMessageBusClient`

Creates and starts a `HiveMessageBusClient` WebSocket connection to this node.

```python
bus = node.connect(key="myaccesskey", crypto_key="mycryptokey")
```

---

## `AbstractDevice`

Internal device descriptor. Holds raw connection parameters (host, port, ssl,
device_type, name). `HiveMindNode` wraps an `AbstractDevice` instance.

### Constructor

```python
AbstractDevice(host, port, device_type, ssl=False, name="HiveMind Node")
```

### Properties

| Property | Type | Description |
|---|---|---|
| `address` | `str` | `"host:port"` |
| `friendly_name` | `str` | Device name |
| `data` | `dict` | `{host, port, ssl, type}` |

---

## HiveBeacon Protocol

**HiveBeacon** is a lightweight UDP broadcast protocol designed specifically for HiveMind mesh discovery.

### Announcement

- **Broadcast address**: `255.255.255.255` (UDP)
- **Port**: `56789`
- **Interval**: Every 2 seconds
- **Payload**: JSON with hub capabilities, network protocols, and configuration metadata
- **Re-read on every cycle**: Changes to `server.json` take effect without restarting

### Discovery

- **Listener port**: `56789` (UDP)
- **Scope**: Local subnet only (broadcast)
- **Deduplication**: Automatic (by host + device name)
- **Conversion**: Raw beacon payloads are converted to `HiveMindNode` objects

### Advantages

- **Zero dependencies** — no external packages
- **Zero configuration** — works out of the box
- **Lightweight** — ~2KB payload every 2 seconds
- **Decentralized** — no central registry or service discovery daemon
- **Mesh-friendly** — designed for distributed HiveMind networks
