# How it works

HiveMind-presence has two roles: **announce** (run on the hub) and **scan** (run
on a satellite or any client that needs to find a hub).

## Announce

`LocalPresence` (CLI: `hivemind-presence announce`) starts an advertiser for each
enabled transport:

- **mDNS**: `ZeroConfAnnounce` registers a Zeroconf service of type
  `--service-type` (default `HiveMind-websocket`) carrying the node name, host,
  port, and SSL flag.
- **UPnP**: `UPNPAnnounce` runs an SSDP server plus a small HTTP server that
  serves a UPnP device descriptor (and SCPD XML) describing the node.

The advertised record contains everything a client needs to connect: friendly
name, host IP, port, and whether SSL is in use.

```
Hub                                  Satellite / client
 │  announce (mDNS + / or UPnP)
 │ ───────────────────────────────▶  scan
 │      name, host, port, ssl         discovers record
 │                                    │
 │                                    │ HiveMindNode.connect(key, crypto_key)
 │ ◀────────── ws://host:port ──────  opens encrypted HiveMind session
```

## Scan

`LocalDiscovery` (CLI: `hivemind-presence scan`) starts a scanner for each enabled
transport and collects discovered nodes:

- `ZeroScanner` browses the mDNS service type and fires `on_new_zeroconf_node`.
- `UPNPScanner` discovers SSDP advertisements and fires `on_new_upnp_node`.

Each discovery is wrapped in a `HiveMindNode` keyed by `host:port` and passed to
the `on_new_node` callback. The `scan(timeout=...)` generator yields each new node
once, until the timeout elapses.

## Connecting

`HiveMindNode.connect(key, crypto_key=None, self_signed=True)` builds a
`HiveMessageBusClient` for the discovered node. It uses `wss://` when the node
advertised SSL, otherwise `ws://`. It runs the client in a thread and returns the
live bus. The access key and crypto key are the node's HiveMind credentials.
Presence does not handle authentication, only locating the address to connect
to.

## Optional dependency behaviour

The `zeroconf` package is LGPL and imported lazily. If it is not installed,
`_init_zeroconf` swallows the `ImportError` and disables the mDNS transport. With
mDNS disabled and `--upnp false`, `LocalDiscovery` raises `ValueError` because no
transport is active. Enable UPnP or install `zeroconf`.

---
[Home](index.md) · [Configuration →](configuration.md)
