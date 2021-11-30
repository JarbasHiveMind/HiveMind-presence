from rich.console import Console
from rich.table import Table

from HiveMind_presence import LocalDiscovery


def scan_and_print():
    table = Table(title="HiveMind Devices")

    table.add_column("Name", justify="center")
    table.add_column("Protocol", justify="center")
    table.add_column("Host", justify="center")
    table.add_column("Port", justify="center")

    console = Console()
    console.print("Scanning....")
    for device in LocalDiscovery().scan(timeout=10):
        proto = "wss" if device.ssl else "ws "
        table.add_row(device.friendly_name, proto, device.host, str(device.port))
        console.print(table)


if __name__ == "__main__":
    scan_and_print()
