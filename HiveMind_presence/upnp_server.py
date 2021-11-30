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

PORT_NUMBER = 8080


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
                <serviceType>urn:jarbasAi:HiveMind:service:Master</serviceType>
                <serviceId>urn:jarbasAi:HiveMind:serviceId:HiveMindNode</serviceId>
                <controlURL>/HiveMind</controlURL>
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
                <friendlyName>{self.server.friendly_name}</friendlyName>
                <manufacturer>{self.server.manufacturer}</manufacturer>
                <manufacturerURL>{self.server.manufacturer_url}</manufacturerURL>
                <modelDescription>{self.server.model_description}</modelDescription>
                <modelName>{self.server.model_name}</modelName>
                <modelNumber>{self.server.model_number}</modelNumber>
                <modelURL>{self.server.model_url}</modelURL>
                <serialNumber>{self.server.serial_number}</serialNumber>
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
        return """<scpd xmlns="urn:schemas-upnp-org:service-1-0">
            <specVersion>
                <major>1</major>
                <minor>0</minor>
            </specVersion>
        </scpd>"""


class UPNPHTTPServerBase(HTTPServer):
    """
    A simple HTTP server that knows the information about a UPnP device.
    """

    def __init__(self, server_address, request_handler_class):
        HTTPServer.__init__(self, server_address, request_handler_class)
        self.port = None
        self.friendly_name = None
        self.manufacturer = None
        self.manufacturer_url = None
        self.model_description = None
        self.model_name = None
        self.model_url = None
        self.serial_number = None
        self.uuid = None
        self.presentation_url = None
        self.scpd_xml_path = None
        self.device_xml_path = None
        self.major_version = None
        self.minor_version = None


class UPNPHTTPServer(threading.Thread):
    """
    A thread that runs UPNPHTTPServerBase.
    """

    def __init__(self, port, friendly_name, manufacturer, manufacturer_url,
                 model_description, model_name,
                 model_number, model_url, serial_number, uuid,
                 presentation_url, host=""):
        threading.Thread.__init__(self, daemon=True)
        self.server = UPNPHTTPServerBase(('', port), UPNPHTTPServerHandler)
        self.server.port = port
        self.server.friendly_name = friendly_name
        self.server.manufacturer = manufacturer
        self.server.manufacturer_url = manufacturer_url
        self.server.model_description = model_description
        self.server.model_name = model_name
        self.server.model_number = model_number
        self.server.model_url = model_url
        self.server.serial_number = serial_number
        self.server.uuid = uuid
        self.server.presentation_url = presentation_url
        self.server.scpd_xml_path = 'scpd.xml'
        self.server.device_xml_path = "device.xml"
        self.server.major_version = 0
        self.server.minor_version = 1
        self.host = host

    @property
    def path(self):
        return f'http://{self.host}:8088/{self.server.device_xml_path}'

    def run(self):
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

    def _get_device_data(self, location):
        LOG.info(f"Fetching Node data: {location}")
        xml = requests.get(location).text
        data = xml2dict(xml)
        services = data["root"]["device"]['serviceList']
        for service in services.values():
            if service["serviceType"] == \
                    'urn:jarbasAi:HiveMind:service:Master':
                data["address"] = service["URLBase"]
                break
        return data

    def run(self) -> None:
        self.running = True
        seen = []
        while self.running:
            devices = upnpclient.discover()
            for d in devices:
                if d.location in self.nodes:
                    continue
                if d.model_name == "HiveMind-core":
                    data = self._get_device_data(d.location)
                    host, port = data["address"].split(":")
                    device = AbstractDevice(name=data["root"]['device']['friendlyName'],
                                            host=host,
                                            port=port,
                                            device_type=data["root"]['device']['modelName'])
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
                 uuid=None,
                 host=None,
                 port=5678,
                 service_type="HiveMind-websocket",
                 name="HiveMind-Node",
                 manufacturer='JarbasAI',
                 manufacturer_url='https://github.com/JarbasHiveMind',
                 model_description='Jarbas HiveMind',
                 model_name="HiveMind-core",
                 model_number="0.9",
                 model_url="https://github.com/JarbasHiveMind/HiveMind-core"):
        self.name = name
        self.port = port
        self.service_type = service_type
        self.host = host or get_ip()
        self.uuid = uuid or str(uuid4())
        self.upnp_server = UPNPHTTPServer(8088,
                                          friendly_name=self.name,
                                          manufacturer=manufacturer,
                                          manufacturer_url=manufacturer_url,
                                          model_description=model_description,
                                          model_name=model_name,
                                          model_number=model_number,
                                          model_url=model_url,
                                          serial_number=self.service_type,
                                          uuid=self.uuid,
                                          presentation_url=f"{self.host}:{self.port}",
                                          host=self.host)
        self.ssdp = SSDPServer()
        self.ssdp.register('local',
                           f'uuid:{self.uuid}::upnp:{self.service_type}',
                           f'upnp:{self.service_type}',
                           self.upnp_server.path)

    @property
    def ssl(self):
        return self.host.startswith("wss://") or \
               self.host.startswith("https://")

    def start(self):
        self.upnp_server.start()
        self.ssdp.start()

    def stop(self):
        self.ssdp.shutdown()
        self.upnp_server.shutdown()
