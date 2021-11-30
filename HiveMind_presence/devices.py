from uuid import uuid4

from hivemind_bus_client import HiveMessageBusClient


class AbstractDevice:
    def __init__(self, host, port, device_type, ssl=False, name="HiveMind Node"):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.device_type = device_type
        self.name = name

    @property
    def services(self):
        return {}

    @property
    def device_name(self):
        return self.name

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
    def udn(self):
        return f"{self.model_name}:{uuid4()}"

    @property
    def address(self):
        return self.host + ":" + str(self.port)

    @property
    def data(self):
        return {"host": self.host,
                "port": self.port,
                "ssl": self.ssl,
                "type": self.device_type}


class HiveMindNode:
    def __init__(self, d=None):
        self.device = d

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
    def device_id(self):
        return self.device.udn

    @property
    def address(self):
        return self.device.address

    @property
    def host(self):
        return self.device.host

    @property
    def port(self):
        return int(self.device.port)

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
