import ipaddress
import time

from zeroconf import ServiceBrowser, ServiceStateChange
from zeroconf import Zeroconf, ServiceInfo

from hivemind_presence.utils import get_ip


class ZeroConfAnnounce:
    def __init__(self,
                 host=None,
                 port=5678,
                 ssl=False,
                 service_type="HiveMind-websocket",
                 name="HiveMind-Node"):
        self.name = name
        self.port = port
        self.service_type = service_type
        self.host = host or get_ip()
        self.ssl = ssl

        self.zero = None
        self.info = ServiceInfo(
            "_http._tcp.local.",
            f" - {self.name}._http._tcp.local.",
            addresses=[ipaddress.ip_address(self.host).packed],
            port=self.port,
            properties={"type": self.service_type,
                        "name": self.name,
                        "ssl": self.ssl,
                        "host": self.host,
                        "port": self.port},
        )

    def start(self):
        """Start advertising to other devices about the ip address"""
        print(f"Announcing node via Zeroconf")
        self.zero = Zeroconf()
        # Registering service
        self.zero.register_service(self.info)

    def stop(self):
        if self.zero:
            self.zero.unregister_service(self.info)
            self.zero.close()
        self.zero = None


class ZeroScanner:
    def __init__(self, identifier="HiveMind-websocket"):
        self.zero = None
        self.browser = None
        self.nodes = {}
        self.running = False
        self.identifier = identifier.encode("utf-8")

    def get_nodes(self):
        return self.nodes

    def on_new_node(self, node):
        node["last_seen"] = time.time()
        self.nodes[f'{node["name"]}:{node["host"]}'] = node

    def on_node_update(self, node):
        node["last_seen"] = time.time()
        self.nodes[f'{node["name"]}:{node["host"]}'] = node

    def on_service_state_change(self, zeroconf, service_type, name,
                                state_change):

        if state_change is ServiceStateChange.Added or state_change is \
                ServiceStateChange.Updated:
            info = zeroconf.get_service_info(service_type, name)
            if info and info.properties:
                for key, value in info.properties.items():
                    if key == b"type" and value == self.identifier:
                        host = info._properties[b"host"].decode("utf-8")
                        port = info._properties[b"port"].decode("utf-8")
                        name = info._properties[b"name"].decode("utf-8")
                        ssl = info._properties[b"ssl"].decode("utf-8")
                        node = {"host": host, "port": port, "name": name, "ssl": ssl}
                        if state_change is ServiceStateChange.Added:
                            self.on_new_node(node)
                        else:
                            self.on_node_update(node)

    def start(self):
        self.zero = Zeroconf()
        self.browser = ServiceBrowser(self.zero, "_http._tcp.local.",
                                      handlers=[self.on_service_state_change])
        self.running = True

    def stop(self):
        if self.zero:
            self.zero.close()
        self.zero = None
        self.browser = None
        self.running = False


if __name__ == "__main__":
    z = ZeroScanner()
    z.start()
    from ovos_utils import wait_for_exit_signal
    wait_for_exit_signal()