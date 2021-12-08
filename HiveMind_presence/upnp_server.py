import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep
from uuid import uuid4

import requests
import upnpclient

from HiveMind_presence.devices import HiveMindNode, AbstractDevice
from HiveMind_presence.ssdp import SSDPServer
from HiveMind_presence.utils import LOG, xml2dict
from HiveMind_presence.utils import get_ip


class UPNPHTTPServerHandler(BaseHTTPRequestHandler):
    """
    A HTTP handler that serves the UPnP XML files.
    """

    # Handler for the GET requests
    def do_GET(self):
        if self.path == "/" + self.server.scpd_xml_path:
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            self.wfile.write(self.scpd_xml.encode())
            return
        if self.path == "/" + self.server.device_xml_path:
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            self.wfile.write(self.device_xml.encode())
            return
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Not found.")
            return

    @property
    def services_xml(self):
        return f"""<serviceList>
            <service>
                <URLBase>{self.server.presentation_url}</URLBase>
                <serviceType>urn:jarbasAi:HiveMind:service:{self.server.service_type}</serviceType>
                <serviceId>urn:jarbasAi:HiveMind:serviceId:{self.server.name}</serviceId>
                <controlURL>/HiveMind</controlURL>
                <ssl>{self.server.ssl}</ssl>
                <host>{self.server.host}</host>
                <port>{self.server.port}</port>
                <eventSubURL/>
                <SCPDURL>{self.server.scpd_xml_path}</SCPDURL>
            </service>
        </serviceList>"""

    @property
    def device_xml(self):
        """
        Get the main device descriptor xml file.
        """
        return f"""<root>
            <specVersion>
                <major>{self.server.major_version}</major>
                <minor>{self.server.minor_version}</minor>
            </specVersion>
            <device>
                <deviceType>urn:schemas-upnp-org:device:Basic:1</deviceType>
                <friendlyName>{self.server.name}</friendlyName>
                <modelName>HiveMind</modelName>
                <UDN>uuid:{self.server.uuid}</UDN>
                {self.services_xml}
                <presentationURL>{self.server.presentation_url}</presentationURL>
            </device>
        </root>"""

    @property
    def scpd_xml(self):
        """
        Get the device WSD file.
        """
        return f"""<scpd xmlns="urn:schemas-upnp-org:service-1-0">
            <specVersion>
                <major>{self.server.major_version}</major>
                <minor>{self.server.minor_version}</minor>
            </specVersion>
        </scpd>"""


class UPNPHTTPServerBase(HTTPServer):
    """
    A simple HTTP server that knows the information about a UPnP device.
    """

    def __init__(self, server_address, request_handler_class):
        HTTPServer.__init__(self, server_address, request_handler_class)
        self.port = 5678
        self.name = "HiveMind-Node"
        self.service_type = "HiveMind-websocket"
        self.host = get_ip()
        self.ssl = False

        self.uuid = str(uuid4())
        self.scpd_xml_path = None
        self.device_xml_path = None
        self.major_version = 0
        self.minor_version = 1

    @property
    def presentation_url(self):
        return f"wss://{self.host}:{self.port}" if self.ssl \
            else f"ws://{self.host}:{self.port}"


class UPNPHTTPServer(threading.Thread):
    """
    A thread that runs UPNPHTTPServerBase.
    """

    def __init__(self, port=5678, friendly_name="HiveMind-Node", ssl=False,
                 service_type="HiveMind-websocket", upnp_port=8088):
        threading.Thread.__init__(self, daemon=True)

        self.server = UPNPHTTPServerBase(('', upnp_port), UPNPHTTPServerHandler)
        self.server.port = port
        self.server.name = friendly_name
        self.server.service_type = service_type
        self.server.ssl = ssl

        self.server.scpd_xml_path = 'scpd.xml'
        self.server.device_xml_path = "device.xml"
        self.server.major_version = 0
        self.server.minor_version = 1

    @property
    def uuid(self):
        return self.server.uuid

    @property
    def service_type(self):
        return self.server.service_type

    @property
    def presentation_url(self):
        return self.server.presentation_url

    @property
    def path(self):
        return f'http://{self.server.host}:8088/{self.server.device_xml_path}'

    def run(self):
        LOG.info(f"Announcing node via UPNP/SSDP: {self.path}")
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


class UPNPScanner(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDaemon(True)
        self.nodes = {}
        self.running = False

    def get_nodes(self):
        return self.nodes

    def on_new_node(self, node):
        self.nodes[node.address] = node

    def on_node_update(self, node):
        self.nodes[node.address] = node

    def _get_node_data(self, location, service_type="HiveMind-websocket"):
        LOG.info(f"Fetching Node data: {location}")
        xml = requests.get(location).text
        data = xml2dict(xml)
        services = data["root"]["device"]['serviceList']
        for service in services.values():
            if service["serviceType"] == f'urn:jarbasAi:HiveMind:service:{service_type}':
                return AbstractDevice(**{
                    "device_type": service_type,
                    "host": service["host"],
                    "port": int(service["port"]),
                    "ssl": service["ssl"] == "True",
                    "name": data["root"]['device']['friendlyName']
                })

    def run(self) -> None:
        self.running = True
        seen = []
        while self.running:
            devices = upnpclient.discover()
            for d in devices:
                if d.location in self.nodes:
                    continue
                if "HiveMind" in d.model_name:
                    device = self._get_node_data(d.location)
                    if not device:
                        continue
                    node = HiveMindNode(device)
                    if node.address not in seen:
                        seen.append(node.address)
                        self.on_new_node(node)
            sleep(1)
        self.stop()

    def stop(self):
        self.running = False


class UPNPAnnounce:
    def __init__(self,
                 port=5678,
                 ssl=False,
                 service_type="HiveMind-websocket",
                 name="HiveMind-Node"):

        self.upnp = UPNPHTTPServer(friendly_name=name,
                                   service_type=service_type,
                                   ssl=ssl, port=port)
        self.ssdp = SSDPServer()
        self.ssdp.register('local',
                           f'uuid:{self.upnp.uuid}::upnp:{self.upnp.service_type}',
                           f'upnp:{self.upnp.service_type}',
                           self.upnp.path)

    def start(self):
        self.upnp.start()
        self.ssdp.start()

    def stop(self):
        self.ssdp.shutdown()
        self.upnp.shutdown()
