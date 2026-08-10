# Configuration reference

## CLI

### `hivemind-presence announce`

Advertise this node on the LAN.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `--port` | int | `5678` | HiveMind WebSocket port to advertise. |
| `--name` | str | `HiveMind-Node` | Friendly device name shown to scanners. |
| `--service-type` | str | `HiveMind-websocket` | Service identifier. Must match the scanner's value. |
| `--zeroconf` | bool | `true` | Advertise via mDNS/Zeroconf. |
| `--upnp` | bool | `false` | Advertise via UPnP/SSDP. |
| `--ssl` | bool | `false` | Report SSL support (scanners connect with `wss://`). |

### `hivemind-presence scan`

Discover nodes on the LAN and print them in a table.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `--zeroconf` | bool | `true` | Scan via mDNS/Zeroconf. |
| `--upnp` | bool | `false` | Scan via UPnP/SSDP. |
| `--service-type` | str | `HiveMind-websocket` | Service identifier to match against announcers. |

## API

### `LocalPresence`

```python
LocalPresence(port=5678, ssl=False, service_type="HiveMind-websocket",
              name="HiveMind-Node", upnp=False, zeroconf=True)
```

| Argument | Default | Description |
| --- | --- | --- |
| `port` | `5678` | Port to advertise. |
| `ssl` | `False` | Advertise SSL support. |
| `service_type` | `HiveMind-websocket` | Service identifier. |
| `name` | `HiveMind-Node` | Friendly device name. |
| `upnp` | `False` | Enable the UPnP transport. |
| `zeroconf` | `True` | Enable the mDNS transport (no-op if `zeroconf` is not installed). |

Methods: `start()`, `stop()`.

### `LocalDiscovery`

```python
LocalDiscovery(zeroconf=True, upnp=True, service_type="HiveMind-websocket")
```

| Argument | Default | Description |
| --- | --- | --- |
| `zeroconf` | `True` | Enable the mDNS scanner. |
| `upnp` | `True` | Enable the UPnP scanner. |
| `service_type` | `HiveMind-websocket` | Service identifier to match. |

Raises `ValueError` if both transports are disabled.

Key members:

- `on_new_node(node)`: assign a callback to react to each discovered node.
- `scan(timeout=25)`: a generator that yields each newly discovered
  `HiveMindNode` once, until `timeout` seconds elapse.
- `nodes`: a dict of `host:port` to `HiveMindNode`, for nodes seen so far.
- `start()` / `stop()`.

### `HiveMindNode`

Wraps a discovered device. Properties: `friendly_name`, `address`, `host`, `port`,
`ssl`, `device_type`.

```python
HiveMindNode.connect(key, crypto_key=None, self_signed=True,
                     useragent="HiveMind-websocket-client")
```

Opens a `HiveMessageBusClient` to the node (`wss://` if the node advertised SSL,
else `ws://`), runs it in a thread, and returns the bus.

---
[← How it works](how-it-works.md) · [Home](index.md) · [Examples →](examples.md)
