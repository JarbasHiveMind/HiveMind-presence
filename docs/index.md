# HiveMind-presence

Local-network presence and discovery for HiveMind nodes. A hub announces itself
so satellites can find it without a hardcoded address; a satellite scans the LAN
to discover reachable hubs and open a connection.

- [How it works](how-it-works.md)
- [Configuration reference](configuration.md)
- [Examples](examples.md)

## Where it sits

HiveMind-presence is the discovery layer of the
[HiveMind](https://github.com/JarbasHiveMind/HiveMind-core) mesh. It does not move
protocol traffic itself — it advertises and locates the WebSocket address of a
[hivemind-core](https://github.com/JarbasHiveMind/HiveMind-core) hub. Once a node
is discovered, the matching client (Python `hivemind-bus-client`, browser, ESP32)
opens the encrypted HiveMind connection.

## Transports

| Transport | Status | Notes |
| --- | --- | --- |
| mDNS / Zeroconf | available, default | Optional `zeroconf` dependency (LGPL). |
| UPnP / SSDP | available, opt-in | Enable with `--upnp true`. |
| HiveBeacon (UDP broadcast) | planned default | Zero-dependency broadcast beacon, becomes the default; mDNS stays optional. |
