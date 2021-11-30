import time

from HiveMind_presence import LocalDiscovery, UPNPAnnounce


def scan_and_print():
    print("|     name      |     host      |  port  |")
    for device in LocalDiscovery().scan():
        print("|", device.friendly_name,
              "|", device.host,
              "| ", device.port, " |")


def announce_zeroconf():
    from HiveMind_presence.zero import ZeroConfAnnounce
    announcer = ZeroConfAnnounce()
    announcer.start()


def announce_upnp():
    announcer = UPNPAnnounce()
    announcer.start()


if __name__ == "__main__":
    # TODO argparse
    scan = True

    if scan:
        scan_and_print()
    else:
        announce_upnp()
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
