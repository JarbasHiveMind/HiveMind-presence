# API Reference — HiveMind-presence

Source: `hivemind_presence/`

---

## `LocalPresence`

```python
from hivemind_presence import LocalPresence
```

Announces a HiveMind hub on the local network using UPnP/SSDP and/or
Zeroconf/mDNS.

### Constructor

```python
LocalPresence(port=5678, name=None, service_type="HiveMind-websocket",
              zeroconf=True, upnp=True, ssl=False)
```

| Parameter | Type | Description |
|---|---|---|
| `port` | `int` | HiveMind server port to advertise |
| `name` | `str` | Device name (defaults to hostname) |
| `service_type` | `str` | Service identifier used in UPnP model name and Zeroconf service properties |
| `zeroconf` | `bool` | Enable Zeroconf/mDNS announcement (requires `zeroconf` package) |
| `upnp` | `bool` | Enable UPnP/SSDP announcement |
| `ssl` | `bool` | Advertise the port as SSL-enabled |

### Methods

#### `start()`

Starts UPnP HTTP server (port 8088 by default) and SSDP multicast announcements,
and/or registers with Zeroconf. Runs until `stop()` is called.

#### `stop()`

Unregisters all announcements and shuts down background threads cleanly.

---

## `LocalDiscovery`

```python
from hivemind_presence import LocalDiscovery
```

Scans the local network for HiveMind hubs announced via UPnP/SSDP and/or
Zeroconf/mDNS.

### Constructor

```python
LocalDiscovery(zeroconf=True, upnp=True, service_type="HiveMind-websocket")
```

| Parameter | Type | Description |
|---|---|---|
| `zeroconf` | `bool` | Enable Zeroconf/mDNS scanning (requires optional `zeroconf` package) |
| `upnp` | `bool` | Enable UPnP scanning |
| `service_type` | `str` | Filter — only nodes matching this type are reported |

Raises `ValueError` if both `zeroconf` and `upnp` are `False`.

Zeroconf is a soft dependency (LGPL). If the `zeroconf` package is not installed,
the Zeroconf scanner is silently disabled and discovery continues with UPnP only.

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `nodes` | `dict[str, HiveMindNode]` | All discovered nodes keyed by `"host:port"` |
| `running` | `bool` | Whether discovery is currently active |

### Methods

#### `start()`

Starts background scanning threads.

#### `scan(timeout=25) -> Generator[HiveMindNode, None, None]`

Starts discovery (if not already running) and yields `HiveMindNode` objects as
they are discovered, for up to `timeout` seconds. Yields each node only once per
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

## Discovery protocols

### UPnP/SSDP

- SSDP multicast on `239.255.255.250:1900`
- UPnP device XML served on HTTP port `8088` (configurable)
- Scanner searches for UPnP devices with `"HiveMind"` in `model_name`
- Works across some routers that forward UPnP multicast between VLANs

### Zeroconf/mDNS

- Service type: `_http._tcp.local.`
- Service properties include: `name`, `host`, `port`, `ssl`, `service_type`
- Requires the `zeroconf` Python package (LGPL licensed — must be installed explicitly)
- Works on the local link only (does not cross routers unless mDNS repeater is configured)
