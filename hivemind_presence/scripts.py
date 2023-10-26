import click
from ovos_utils import wait_for_exit_signal
from rich.console import Console
from rich.table import Table

from hivemind_presence.devices import HiveMindNode
from hivemind_presence.discovery import LocalDiscovery
from hivemind_presence.presence import LocalPresence


@click.group()
def hmpresence_cmds():
    pass


@hmpresence_cmds.command(help="Advertise node in the local network", name="announce")
@click.option("--port", required=False, type=int, default=5678,
              help="HiveMind port number (default: 5678)")
@click.option("--name", required=False, type=str, default="HiveMind-Node",
              help="friendly device name (default: HiveMind-Node)")
@click.option("--service-type", required=False, type=str, default="HiveMind-websocket",
              help="HiveMind service type (default: HiveMind-websocket)")
@click.option("--zeroconf", required=False, type=bool, default=True, help="advertise via zeroconf (default: True)")
@click.option("--upnp", required=False, type=bool, default=False, help="advertise via UPNP (default: False)")
@click.option("--ssl", required=False, type=bool, default=False, help="report ssl support (default: False)")
def announce(port, name, service_type, zeroconf, upnp, ssl):
    announcer = LocalPresence(port=port, ssl=ssl, service_type=service_type, name=name, zeroconf=zeroconf, upnp=upnp)
    announcer.start()
    wait_for_exit_signal()
    announcer.stop()


@hmpresence_cmds.command(help="scan for hivemind nodes in the local network", name="scan")
@click.option("--zeroconf", required=False, type=bool, default=True, help="scan via zeroconf (default: True)")
@click.option("--upnp", required=False, type=bool, default=False, help="scan via UPNP (default: False)")
@click.option("--service-type", required=False, type=str, default="HiveMind-websocket",
              help="HiveMind service type (default: HiveMind-websocket)")
def scan(zeroconf, upnp, service_type):
    console = Console()

    discovery = LocalDiscovery(zeroconf=zeroconf, upnp=upnp, service_type=service_type)

    table = Table(title="HiveMind Nodes")
    table.add_column("Friendly Name", justify="right", no_wrap=True)
    table.add_column("Host")
    table.add_column("Port")

    def print_node(node: HiveMindNode):
        console.clear()

        table.add_row(node.friendly_name,
                      node.host,
                      str(node.port))

        console.print(table)

    discovery.on_new_node = print_node

    discovery.start()
    wait_for_exit_signal()
    discovery.stop()


if __name__ == "__main__":
    hmpresence_cmds()
