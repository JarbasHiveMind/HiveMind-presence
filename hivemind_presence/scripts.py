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
@click.option("--ssl", required=False, type=bool, default=False,
              help="report ssl support (default: False)")
def announce(port, name, service_type, ssl):
    """
    Announce a local HiveMind service on the network.
    
    Starts a LocalPresence instance that advertises the given service parameters and runs until a termination signal is received.
    
    Parameters:
        port (int): TCP port the service listens on.
        name (str): Friendly name to advertise for the node.
        service_type (str): Service type identifier used for discovery (e.g., "HiveMind-websocket").
        ssl (bool): Whether the advertised service uses SSL; advertised as the node's SSL state.
    """
    announcer = LocalPresence(
        port=port, ssl=ssl,
        service_type=service_type,
        name=name,
    )
    announcer.start()
    wait_for_exit_signal()
    announcer.stop()


@hmpresence_cmds.command(help="scan for hivemind nodes in the local network", name="scan")
@click.option("--service-type", required=False, type=str, default="HiveMind-websocket",
              help="HiveMind service type (default: HiveMind-websocket)")
@click.option("--timeout", required=False, type=float, default=25.0,
              help="scan duration in seconds (default: 25)")
def scan(service_type, timeout):
    """
    Start local discovery for HiveMind nodes and display discovered nodes in a Rich table until an exit signal is received.
    
    Parameters:
        service_type (str): Service type to discover (e.g., "HiveMind-websocket").
        timeout (float): Desired scan duration in seconds. Note: this parameter is accepted but is not currently applied by the discovery loop.
    """
    console = Console()

    discovery = LocalDiscovery(service_type=service_type)

    table = Table(title="HiveMind Nodes")
    table.add_column("Friendly Name", justify="right", no_wrap=True)
    table.add_column("Host")
    table.add_column("Port")
    table.add_column("SSL")

    def print_node(node: HiveMindNode):
        """
        Update the console table to show a discovered HiveMind node.
        
        Adds the node's friendly name, host, port, and SSL state as a new row and reprints the table to the console.
        
        Parameters:
            node (HiveMindNode): Discovered node whose details will be added to the display table.
        """
        console.clear()
        table.add_row(
            node.friendly_name,
            node.host,
            str(node.port),
            str(node.ssl),
        )
        console.print(table)

    discovery.on_new_node = print_node

    discovery.start()
    wait_for_exit_signal()
    discovery.stop()


if __name__ == "__main__":
    hmpresence_cmds()
