"""TP-Link adapter for Mozilla IoT Gateway."""

from gateway_addon import Adapter, Device, Property
from os import path
import functools
import gateway_addon
import signal
import sys
import threading
import time

sys.path.append(path.join(path.dirname(path.abspath(__file__)), 'lib'))
from pyHS100 import Discover, SmartBulb, SmartPlug  # flake8: noqa


_API_VERSION = {
    'min': 1,
    'max': 1,
}
_ADAPTER = None
_TIMEOUT = 3
_POLL_INTERVAL = 5

print = functools.partial(print, flush=True)


class TPLinkProperty(Property):
    """TP-Link property type."""

    def __init__(self, device, name, description, value):
        """
        Initialize the object.

        device -- the Device this property belongs to
        name -- name of the property
        description -- description of the property, as a dictionary
        value -- current value of this property
        """
        Property.__init__(self, device, name, description)
        self.set_cached_value(value)

    def set_value(self, value):
        """
        Set the current value of the property.

        value -- the value to set
        """
        if self.name == 'on':
            self.device.hs100_dev.state = 'ON' if value else 'OFF'
        else:
            return

        self.set_cached_value(value)
        self.device.notify_property_changed(self)

    def poll(self):
        """Poll the current value and update if necessary."""
        if self.name == 'on':
            value = self.device.hs100_dev.is_on
        else:
            return

        if value != self.value:
            self.set_cached_value(value)
            self.device.notify_property_changed(self)


class TPLinkDevice(Device):
    """TP-Link device type."""

    def __init__(self, adapter, _id, hs100_dev):
        """
        Initialize the object.

        adapter -- the Adapter managing this device
        hs100_dev -- the pyHS100 device object to initialize from
        """
        Device.__init__(self, adapter, _id)

        self.hs100_dev = hs100_dev
        self.description = hs100_dev.model
        self.name = hs100_dev.alias
        if not self.name:
            self.name = self.description

        if isinstance(hs100_dev, SmartPlug):
            self.type = 'onOffSwitch'
            self.properties['on'] = TPLinkProperty(
                self, 'on', {'type': 'boolean'}, hs100_dev.is_on)
            # TODO: power consumption
        elif isinstance(hs100_dev, SmartBulb):
            self.type = 'onOffSwitch'
            self.properties['on'] = TPLinkProperty(
                self, 'on', {'type': 'boolean'}, hs100_dev.is_on)
            # TODO: power consumption, color, brightness, temperature
        else:
            self.type = 'unknown'

        t = threading.Thread(target=self.poll)
        t.daemon = True
        t.start()

    def poll(self):
        """Poll the device for changes."""
        while True:
            time.sleep(_POLL_INTERVAL)

            for prop in self.properties.values():
                prop.poll()


class TPLinkAdapter(Adapter):
    """Adapter for TP-Link smart home devices."""

    def __init__(self, verbose=False):
        """
        Initialize the object.

        verbose -- whether or not to enable verbose logging
        """
        self.name = self.__class__.__name__
        Adapter.__init__(self,
                         'tplink-adapter',
                         'tplink-adapter',
                         verbose=verbose)

        self.pairing = False
        self.start_pairing(_TIMEOUT)

    def start_pairing(self, timeout):
        """
        Start the pairing process.

        timeout -- Timeout in seconds at which to quit pairing
        """
        self.pairing = True
        for dev in Discover.discover(timeout=min(timeout, _TIMEOUT)).values():
            if not self.pairing:
                break

            _id = 'tplink-' + dev.sys_info['deviceId']
            if _id not in self.devices:
                device = TPLinkDevice(self, _id, dev)
                if device.type == 'unknown':
                    continue

                self.handle_device_added(device)

    def cancel_pairing(self):
        """Cancel the pairing process."""
        self.pairing = False


def cleanup(signum, frame):
    """Clean up any resources before exiting."""
    if _ADAPTER is not None:
        _ADAPTER.close_proxy()

    sys.exit(0)


if __name__ == '__main__':
    if gateway_addon.API_VERSION < _API_VERSION['min'] or \
            gateway_addon.API_VERSION > _API_VERSION['max']:
        print('Unsupported API version.')
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    _ADAPTER = TPLinkAdapter(verbose=True)

    # Wait until the proxy stops running, indicating that the gateway shut us
    # down.
    while _ADAPTER.proxy_running():
        time.sleep(5)
