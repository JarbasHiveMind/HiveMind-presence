import requests
from hivemind_bus_client import HiveMessageBusClient
from HiveMind_presence.utils import LOG, xml2dict


class Device:
    def __init__(self, host, device_type='HiveMind-websocket'):
        self.host = host
        self.device_type = device_type

    @property
    def services(self):
        return {}

    @property
    def location(self):
        return None

    @property
    def device_name(self):
        return self.host

    @property
    def friendly_name(self):
        return self.device_name

    @property
    def model_description(self):
        return self.device_name

    @property
    def model_name(self):
        return self.device_type

    @property
    def model_number(self):
        return "0.1"

    @property
    def udn(self):
        return self.model_name + ":" + self.model_number

    @property
    def address(self):
        return self.location

    @property
    def data(self):
        return {"host": self.host,
                "type": self.device_type}


class HiveMindNode:
    def __init__(self, d=None):
        self.device = d
        self._data = None

    @property
    def services(self):
        return self.device.service_map

    @property
    def xml(self):
        return self.device.location

    @property
    def device_name(self):
        return self.device.device_name

    @property
    def friendly_name(self):
        return self.device.friendly_name

    @property
    def description(self):
        return self.device.model_description

    @property
    def node_type(self):
        return self.device.model_name

    @property
    def version(self):
        return self.device.model_number

    @property
    def device_id(self):
        return self.device.udn

    @property
    def data(self):
        if self.xml and self._data is None:
            LOG.info(f"Fetching Node data: {self.xml}")
            xml = requests.get(self.xml).text
            self._data = xml2dict(xml)
        return self._data

    @property
    def address(self):
        try:
            if self.device.location:
                services = self.data["root"]["device"]['serviceList']
                for service in services.values():
                    if service["serviceType"] == \
                            'urn:jarbasAi:HiveMind:service:Master':
                        return service["URLBase"]
        except:
            pass
        return self.device.data.get("host")

    @property
    def host(self):
        return ":".join(self.address.split(":")[:-1])

    @property
    def port(self):
        return int(self.address.split(":")[-1])

    def connect(self, key, crypto_key=None, self_signed=True):
        ssl = self.address.startswith("wss://") or \
              self.address.startswith("https://")
        bus = HiveMessageBusClient(key=key,
                                   crypto_key=crypto_key,
                                   host=self.host, port=self.port,
                                   useragent=self.device_name,
                                   ssl=ssl,
                                   self_signed=self_signed)
        bus.run_in_thread()
        return bus
