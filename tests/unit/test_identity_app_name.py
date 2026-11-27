"""A discovered node connects with a named identity (HIVEMIND-CRYPTO-1 §2)."""
from unittest.mock import MagicMock, patch

from hivemind_presence import devices
from hivemind_presence.devices import AbstractDevice, HiveMindNode


def _node():
    return HiveMindNode(AbstractDevice("127.0.0.1", 5678, "HiveMind-websocket"))


def test_connect_builds_the_client_with_a_named_identity():
    identity = MagicMock()
    with patch.object(devices, "NodeIdentity", return_value=identity) as ctor, \
         patch.object(devices, "HiveMessageBusClient") as client:
        _node().connect("key")
    ctor.assert_called_once_with(app_name="hivemind-presence")
    assert client.call_args.kwargs["identity"] is identity


def test_a_given_identity_is_used_as_is():
    identity = MagicMock()
    with patch.object(devices, "NodeIdentity") as ctor, \
         patch.object(devices, "HiveMessageBusClient") as client:
        _node().connect("key", identity=identity)
    ctor.assert_not_called()
    assert client.call_args.kwargs["identity"] is identity
