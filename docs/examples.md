# Examples

## Announce a hub

CLI:

```bash
hivemind-presence announce --port 5678 --name living_room
```

Programmatically, alongside a running hub:

```python
from hivemind_presence import LocalPresence

presence = LocalPresence(port=5678, name="living_room")
presence.start()
try:
    run_my_hub()          # block here while the hub runs
finally:
    presence.stop()
```

## Scan and print nodes

```bash
hivemind-presence scan
```

## Discover, then connect

```python
from hivemind_presence import LocalDiscovery

disc = LocalDiscovery()
for node in disc.scan(timeout=25):
    print(f"found {node.friendly_name} at {node.address}")
    bus = node.connect(key="my-access-key", crypto_key="my-crypto-key")
    # `bus` is a running HiveMessageBusClient connected to the hub
    break
disc.stop()
```

## React to nodes via callback

```python
from hivemind_presence import LocalDiscovery, HiveMindNode

disc = LocalDiscovery()

def on_node(node: HiveMindNode):
    print("new node:", node.friendly_name, node.address)

disc.on_new_node = on_node
disc.start()
# ... keep the process alive ...
disc.stop()
```

## Enable UPnP as well as mDNS

```bash
hivemind-presence announce --name kitchen --upnp true
hivemind-presence scan --upnp true
```
