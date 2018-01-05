from os import path
import json
import sys

sys.path.append(path.join(path.dirname(path.abspath(__file__)), 'lib'))

import nnpy  # noqa: E402


_IPC_BASE = 'ipc:///tmp/'


class IpcClient:

    def __init__(self, plugin_id, verbose=False):
        self.manager_socket = nnpy.Socket(nnpy.AF_SP, nnpy.REQ)
        self.manager_conn = \
            self.manager_socket.connect(_IPC_BASE + 'gateway.addonManager')

        if verbose:
            print('IpcClient: Connected to server, registering...')

        self.manager_socket.send(json.dumps({
            'messageType': 'registerPlugin',
            'data': {
                'pluginId': plugin_id,
            }
        }))

        resp = self.manager_socket.recv()
        if verbose:
            print('IpcClient: Received manager message:', resp)

        try:
            resp = json.loads(resp)
            if not resp or 'messageType' not in resp or \
                    resp['messageType'] != 'registerPluginReply':
                raise ValueError()

            self.plugin_socket = nnpy.Socket(nnpy.AF_SP, nnpy.PAIR)
            self.plugin_conn = self.plugin_socket.connect(
                _IPC_BASE + resp['data']['ipcBaseAddr'])

            if verbose:
                print('IpcClient: Registered with PluginServer')
        except ValueError:
            print('IpcClient: Unexpected registration reply from gateway:',
                  resp)
