from uuid import uuid4

from hivemind_bus_client import HiveMessageBusClient


class AbstractDevice:
    def __init__(self, host, port, device_type, ssl=False, name="HiveMind Node"):
        self.host = host
        self.port = port
        if isinstance(ssl, str):
            ssl = ssl.lower() != "false"
        self.ssl = ssl if isinstance(ssl, bool) else False
        self.device_type = device_type
        self.name = name
        self.uuid = str(uuid4())

    @property
    def friendly_name(self):
        return self.name

    @property
    def address(self):
        return f"{self.host}:{self.port}"

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
    def friendly_name(self):
        return self.device.name

    @property
    def address(self):
        return self.device.address

    @property
    def device_type(self):
        return self.device.device_type

    @property
    def host(self):
        return self.device.host

    @property
    def port(self):
        return int(self.device.port)

    @property
    def ssl(self):
        return self.device.ssl

    def connect(self, key, crypto_key=None, self_signed=True,
                useragent="HiveMind-websocket-client"):
        if self.ssl:
            host = f"wss://{self.host}"
        else:
            host = f"ws://{self.host}"
        bus = HiveMessageBusClient(key=key,
                                   crypto_key=crypto_key,
                                   host=host, port=self.port,
                                   useragent=useragent,
                                   self_signed=self_signed)
        bus.run_in_thread()
        return bus
