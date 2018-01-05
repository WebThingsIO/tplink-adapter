from addon_manager_proxy import AddonManagerProxy
from ipc import IpcClient


class Adapter:

    def __init__(self, _id, package_name, verbose=False):
        self.id = _id
        self.package_name = package_name
        self.devices = {}
        self.actions = {}

        # We assume that the adapter is ready right away. If, for some reason,
        # a particular adapter needs some time, then it should set ready to
        # False in it's constructor.
        self.ready = True

        self.ipc_client = IpcClient(self.id, verbose=verbose)
        self.manager_proxy = AddonManagerProxy(self.ipc_client.plugin_socket,
                                               self.id,
                                               verbose=verbose)
        self.manager_proxy.add_adapter(self)

    def dump(self):
        print('Adapter:', self.name, '- dump() not implemented')

    def get_id(self):
        return self.id

    def get_package_name(self):
        return self.package_name

    def get_device(self, device_id):
        return self.devices.get(device_id, None)

    def get_devices(self):
        return self.devices

    def get_name(self):
        return self.name

    def is_ready(self):
        return self.ready

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ready': self.ready,
        }

    def handle_device_added(self, device):
        self.devices[device.id] = device
        self.manager_proxy.handle_device_added(device)

    def handle_device_removed(self, device):
        if device.id in self.devices:
            del self.devices[device.id]

        self.manager_proxy.handle_device_removed(device)

    def start_pairing(self, timeout):
        print('Adapter:', self.name, 'id', self.id, 'pairing started')

    def cancel_pairing(self):
        print('Adapter:', self.name, 'id', self.id, 'pairing cancelled')

    def remove_thing(self, device_id):
        device = self.get_device(device_id)
        if device:
            print('Adapter:', self.name, 'id', self.id,
                  'remove_thing(' + device.id + ')')

    def cancel_remove_thing(self, device_id):
        device = self.get_device(device_id)
        if device:
            print('Adapter:', self.name, 'id', self.id,
                  'cancel_remove_thing(' + device.id + ')')

    def unload(self):
        print('Adapter:', self.name, 'unloaded')
