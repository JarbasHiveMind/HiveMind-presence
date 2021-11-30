import time

from HiveMind_presence import UPNPAnnounce


def announce_zeroconf(ssl=False, port=5678, name="HiveMind-Node", service="HiveMind-websocket"):
    from HiveMind_presence.zero import ZeroConfAnnounce
    announcer = ZeroConfAnnounce(port=port, name=name, service_type=service, ssl=ssl)
    announcer.start()


def announce_upnp(ssl=False, port=5678, name="HiveMind-Node", service="HiveMind-websocket"):
    announcer = UPNPAnnounce(port=port, name=name, service_type=service, ssl=ssl)
    announcer.start()


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="HiveMind port number (default: 5678)", default=5678)
    parser.add_argument("--ssl", help="use wss://", action='store_true')
    parser.add_argument("--zeroconf", help="use zeroconf", action='store_true')
    parser.add_argument("--name", help="friendly device name (default: HiveMind-Node)",
                        default="HiveMind-Node")
    parser.add_argument("--service", help="HiveMind service type (default: HiveMind-websocket)",
                        default="HiveMind-websocket")

    kwargs = parser.parse_args().__dict__
    if kwargs.pop("zeroconf"):
        announce_zeroconf(**kwargs)
    else:
        announce_upnp(**kwargs)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()