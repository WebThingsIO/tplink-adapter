"""TP-Link adapter for WebThings Gateway."""

from gateway_addon import Device
from pyHS100 import SmartDevice, SmartDeviceException
import threading
import time

from .tplink_property import TPLinkBulbProperty, TPLinkPlugProperty
from .util import hsv_to_rgb


_POLL_INTERVAL = 5


class TPLinkDevice(Device):
    """TP-Link device type."""

    def __init__(self, adapter, _id, hs100_dev, index=-1):
        """
        Initialize the object.

        adapter -- the Adapter managing this device
        _id -- ID of this device
        hs100_dev -- the pyHS100 device object to initialize from
        index -- index inside parent device
        """
        Device.__init__(self, adapter, _id)
        self._type = []

        self.hs100_dev = hs100_dev
        self.index = index
        self.description = hs100_dev.sys_info['model']

        if index >= 0:
            self.name = hs100_dev.sys_info['children'][index]['alias']
        else:
            self.name = hs100_dev.sys_info['alias']

        if not self.name:
            self.name = self.description

        t = threading.Thread(target=self.poll)
        t.daemon = True
        t.start()

    @staticmethod
    def power(emeter):
        """
        Determine the current power usage, in watts.

        emeter -- current emeter dict for the device
        """
        if 'power' in emeter:
            return emeter['power']

        if 'power_mw' in emeter:
            return emeter['power_mw'] / 1000

        return None

    @staticmethod
    def voltage(emeter):
        """
        Determine the current voltage, in volts.

        emeter -- current emeter dict for the device
        """
        if 'voltage' in emeter:
            return emeter['voltage']

        if 'voltage_mv' in emeter:
            return emeter['voltage_mv'] / 1000

        return None

    @staticmethod
    def current(emeter):
        """
        Determine the current current, in amperes.

        emeter -- current emeter dict for the device
        """
        if 'current' in emeter:
            return emeter['current']

        if 'current_ma' in emeter:
            return emeter['current_ma'] / 1000

        return None


class TPLinkPlug(TPLinkDevice):
    """TP-Link smart plug type."""

    def __init__(self, adapter, _id, hs100_dev, index=-1):
        """
        Initialize the object.

        adapter -- the Adapter managing this device
        _id -- ID of this device
        hs100_dev -- the pyHS100 device object to initialize from
        index -- index inside parent device
        """
        TPLinkDevice.__init__(self,
                              adapter,
                              _id,
                              hs100_dev,
                              index=index)
        self._type.append('OnOffSwitch')

        sysinfo = hs100_dev.sys_info

        if 'dev_name' not in sysinfo or \
                'Light Switch' not in sysinfo['dev_name']:
            self._type.append('SmartPlug')

        if self.has_emeter(sysinfo):
            # emeter comes via a separate API call, so use it.
            emeter = hs100_dev.get_emeter_realtime()

            power = self.power(emeter)
            if power is not None:
                self._type.append('EnergyMonitor')

                self.properties['instantaneousPower'] = TPLinkPlugProperty(
                    self,
                    'instantaneousPower',
                    {
                        '@type': 'InstantaneousPowerProperty',
                        'title': 'Power',
                        'type': 'number',
                        'unit': 'watt',
                    },
                    power
                )

            voltage = self.voltage(emeter)
            if voltage is not None:
                self.properties['voltage'] = TPLinkPlugProperty(
                    self,
                    'voltage',
                    {
                        '@type': 'VoltageProperty',
                        'title': 'Voltage',
                        'type': 'number',
                        'unit': 'volt',
                    },
                    voltage
                )

            current = self.current(emeter)
            if current is not None:
                self.properties['current'] = TPLinkPlugProperty(
                    self,
                    'current',
                    {
                        '@type': 'CurrentProperty',
                        'title': 'Current',
                        'type': 'number',
                        'unit': 'ampere',
                    },
                    current
                )

        if self.is_dimmable(sysinfo):
            self._type.append('MultiLevelSwitch')
            self.properties['level'] = TPLinkPlugProperty(
                self,
                'level',
                {
                    '@type': 'LevelProperty',
                    'title': 'Level',
                    'type': 'integer',
                    'unit': 'percent',
                    'minimum': 0,
                    'maximum': 100,
                },
                self.brightness(sysinfo)
            )

        self.properties['on'] = TPLinkPlugProperty(
            self,
            'on',
            {
                '@type': 'OnOffProperty',
                'title': 'On/Off',
                'type': 'boolean',
            },
            self.is_on(sysinfo)
        )

        self.properties['led-on'] = TPLinkPlugProperty(
            self,
            'led-on',
            {
                'title': 'LED On/Off',
                'type': 'boolean',
            },
            self.is_led_on(sysinfo)
        )

    def poll(self):
        """Poll the device for changes."""
        while True:
            time.sleep(_POLL_INTERVAL)

            try:
                sysinfo = self.hs100_dev.sys_info
                if sysinfo is None:
                    continue

                emeter = None
                if self.has_emeter(sysinfo):
                    emeter = self.hs100_dev.get_emeter_realtime()

                for prop in self.properties.values():
                    prop.update(sysinfo, emeter)
            except SmartDeviceException:
                continue

    @staticmethod
    def has_emeter(sysinfo):
        """
        Determine whether or not the plug has power monitoring.

        sysinfo -- current sysinfo dict for the device
        """
        features = sysinfo['feature'].split(':')
        return SmartDevice.FEATURE_ENERGY_METER in features

    def is_on(self, sysinfo):
        """
        Determine whether or not the switch is on.

        sysinfo -- current sysinfo dict for the device
        """
        if self.index >= 0:
            return bool(sysinfo['children'][self.index]['state'])

        return bool(sysinfo['relay_state'])

    @staticmethod
    def is_led_on(sysinfo):
        """
        Determine whether or not the LED is on.

        sysinfo -- current sysinfo dict for the device
        """
        return bool(1 - sysinfo['led_off'])

    @staticmethod
    def is_dimmable(sysinfo):
        """
        Determine whether or not the switch is dimmable.

        sysinfo -- current sysinfo dict for the device
        """
        return 'brightness' in sysinfo

    @staticmethod
    def brightness(sysinfo):
        """
        Determine the current level of the switch.

        sysinfo -- current sysinfo dict for the device
        """
        return int(sysinfo['brightness'])


class TPLinkBulb(TPLinkDevice):
    """TP-Link smart bulb type."""

    def __init__(self, adapter, _id, hs100_dev, index=-1):
        """
        Initialize the object.

        adapter -- the Adapter managing this device
        _id -- ID of this device
        hs100_dev -- the pyHS100 device object to initialize from
        index -- index inside parent device
        """
        TPLinkDevice.__init__(self,
                              adapter,
                              _id,
                              hs100_dev,
                              index=index)
        self._type.extend(['OnOffSwitch', 'Light'])

        # Light state, i.e. color, brightness, on/off, comes via a separate API
        # call, so use it.
        state = hs100_dev.get_light_state()
        sysinfo = hs100_dev.sys_info

        if self.is_color(sysinfo):
            self._type.append('ColorControl')

            self.properties['color'] = TPLinkBulbProperty(
                self,
                'color',
                {
                    '@type': 'ColorProperty',
                    'title': 'Color',
                    'type': 'string',
                },
                hsv_to_rgb(*self.hsv(state))
            )

        if self.is_variable_color_temp(sysinfo):
            if 'ColorControl' not in self._type:
                self._type.append('ColorControl')

            temp_range = hs100_dev.valid_temperature_range

            self.properties['colorTemperature'] = TPLinkBulbProperty(
                self,
                'colorTemperature',
                {
                    '@type': 'ColorTemperatureProperty',
                    'title': 'Color Temperature',
                    'type': 'integer',
                    'unit': 'kelvin',
                    'minimum': temp_range[0],
                    'maximum': temp_range[1],
                },
                self.color_temp(state)
            )

        if self.is_color(sysinfo) and self.is_variable_color_temp(sysinfo):
            self.properties['colorMode'] = TPLinkBulbProperty(
                self,
                'colorMode',
                {
                    '@type': 'ColorModeProperty',
                    'title': 'Color Mode',
                    'type': 'string',
                    'enum': [
                        'color',
                        'temperature',
                    ],
                    'readOnly': True,
                },
                self.color_mode(state)
            )

        if self.is_dimmable(sysinfo):
            self.properties['level'] = TPLinkBulbProperty(
                self,
                'level',
                {
                    '@type': 'BrightnessProperty',
                    'title': 'Brightness',
                    'type': 'integer',
                    'unit': 'percent',
                    'minimum': 0,
                    'maximum': 100,
                },
                self.brightness(state)
            )

        # emeter comes via a separate API call, so use it.
        emeter = hs100_dev.get_emeter_realtime()

        power = self.power(emeter)
        if power is not None:
            self._type.append('EnergyMonitor')

            self.properties['instantaneousPower'] = TPLinkBulbProperty(
                self,
                'instantaneousPower',
                {
                    '@type': 'InstantaneousPowerProperty',
                    'title': 'Power',
                    'type': 'number',
                    'unit': 'watt',
                },
                power
            )

        voltage = self.voltage(emeter)
        if voltage is not None:
            self.properties['voltage'] = TPLinkBulbProperty(
                self,
                'voltage',
                {
                    '@type': 'VoltageProperty',
                    'title': 'Voltage',
                    'type': 'number',
                    'unit': 'volt',
                },
                voltage
            )

        current = self.current(emeter)
        if current is not None:
            self.properties['current'] = TPLinkBulbProperty(
                self,
                'current',
                {
                    '@type': 'CurrentProperty',
                    'title': 'Current',
                    'type': 'number',
                    'unit': 'ampere',
                },
                current
            )

        self.properties['on'] = TPLinkBulbProperty(
            self,
            'on',
            {
                '@type': 'OnOffProperty',
                'title': 'On/Off',
                'type': 'boolean',
            },
            self.is_on(state)
        )

    def poll(self):
        """Poll the device for changes."""
        while True:
            time.sleep(_POLL_INTERVAL)

            try:
                sysinfo = self.hs100_dev.sys_info
                if sysinfo is None:
                    continue

                emeter = self.hs100_dev.get_emeter_realtime()
                state = self.hs100_dev.get_light_state()

                for prop in self.properties.values():
                    prop.update(sysinfo, state, emeter)
            except SmartDeviceException:
                continue

    @staticmethod
    def is_dimmable(sysinfo):
        """
        Determine whether or not the light is dimmable.

        sysinfo -- current sysinfo dict for the device
        """
        return bool(sysinfo['is_dimmable'])

    @staticmethod
    def is_color(sysinfo):
        """
        Determine whether or not the light is color-changing.

        sysinfo -- current sysinfo dict for the device
        """
        return bool(sysinfo['is_color'])

    @staticmethod
    def is_variable_color_temp(sysinfo):
        """
        Determine whether or not the light is color-temp-changing.

        sysinfo -- current sysinfo dict for the device
        """
        return bool(sysinfo['is_variable_color_temp'])

    @staticmethod
    def is_on(light_state):
        """
        Determine whether or not the light is on.

        light_state -- current state of the light
        """
        return bool(light_state['on_off'])

    @staticmethod
    def color_temp(light_state):
        """
        Determine the current color temperature.

        light_state -- current state of the light
        """
        if not TPLinkBulb.is_on(light_state):
            light_state = light_state['dft_on_state']

        return int(light_state['color_temp'])

    @staticmethod
    def color_mode(light_state):
        """
        Determine the current color mode.

        light_state -- current state of the light
        """
        if not TPLinkBulb.is_on(light_state):
            light_state = light_state['dft_on_state']

        if int(light_state['color_temp']) == 0:
            return 'color'

        return 'temperature'

    @staticmethod
    def hsv(light_state):
        """
        Determine the current color of the light.

        light_state -- current state of the light
        """
        if not TPLinkBulb.is_on(light_state):
            light_state = light_state['dft_on_state']

        hue = light_state['hue']
        saturation = light_state['saturation']
        value = int(light_state['brightness'] * 255 / 100)

        return hue, saturation, value

    @staticmethod
    def brightness(light_state):
        """
        Determine the current brightness of the light.

        light_state -- current state of the light
        """
        if not TPLinkBulb.is_on(light_state):
            light_state = light_state['dft_on_state']

        return int(light_state['brightness'])
