# HiveMind Presence

Lightweight local network discovery and announcement for HiveMind hubs and satellites via HiveBeacon UDP broadcast.

## Quick Start

### Announce a Hub

```bash
hivemind-presence announce --name "Kitchen Hub" --port 5678
```

**Options:**
- `--name TEXT` — Hub friendly name (default: `HiveMind-Node`)
- `--port INTEGER` — Hub port (default: `5678`)
- `--service-type TEXT` — Service identifier (default: `HiveMind-websocket`)
- `--ssl BOOLEAN` — Report SSL support (default: `False`)

### Discover Hubs

```bash
$ hivemind-presence scan
            HiveMind Nodes
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Friendly Name ┃ Host         ┃ Port   ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━┩
│   living_room │ 192.168.1.9  │ 5678   │
│       kitchen │ 192.168.1.13 │ 5678   │
└───────────────┴──────────────┴────────┘
```

**Options:**
- `--service-type TEXT` — Filter by service type (default: `HiveMind-websocket`)
- `--timeout FLOAT` — Scan duration in seconds (default: `25`)

## How It Works

**HiveBeacon** broadcasts hub information every 2 seconds via UDP multicast on port 56789. No setup, no external dependencies, zero configuration.

For Python integration, see [docs/api.md](docs/api.md).