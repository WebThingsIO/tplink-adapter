"""TP-Link adapter for WebThings Gateway."""

from gateway_addon import Adapter, Database
from pyHS100 import Discover, SmartBulb, SmartPlug, SmartStrip

from .tplink_device import TPLinkBulb, TPLinkPlug


_TIMEOUT = 3


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

    def _add_from_config(self):
        """Attempt to add all configured devices."""
        database = Database('tplink-adapter')
        if not database.open():
            return

        config = database.load_config()
        database.close()

        if not config or 'addresses' not in config:
            return

        for address in config['addresses']:
            try:
                dev = Discover.discover_single(address)
            except (OSError, UnboundLocalError) as e:
                print('Failed to connect to {}: {}'.format(address, e))
                continue

            if dev:
                self._add_device(dev)

    def start_pairing(self, timeout):
        """
        Start the pairing process.

        timeout -- Timeout in seconds at which to quit pairing
        """
        if self.pairing:
            return

        self.pairing = True

        self._add_from_config()

        for dev in Discover.discover(timeout=min(timeout, _TIMEOUT)).values():
            if not self.pairing:
                break

            self._add_device(dev)

        self.pairing = False

    def _add_device(self, dev):
        """
        Add the given device, if necessary.

        dev -- the device object from pyHS100
        """
        if isinstance(dev, SmartStrip):
            for idx, plug in dev.plugs.items():
                _id = 'tplink-' + dev.sys_info['children'][idx]['id']
                if _id not in self.devices:
                    device = TPLinkPlug(self, _id, plug, index=idx)
                    self.handle_device_added(device)

            return

        _id = 'tplink-' + dev.sys_info['deviceId']
        if _id not in self.devices:
            if isinstance(dev, SmartPlug):
                device = TPLinkPlug(self, _id, dev)
            elif isinstance(dev, SmartBulb):
                device = TPLinkBulb(self, _id, dev)
            else:
                return

            self.handle_device_added(device)

    def cancel_pairing(self):
        """Cancel the pairing process."""
        self.pairing = False
