"""TP-Link adapter for WebThings Gateway."""

from gateway_addon import Property
from pyHS100 import SmartDeviceException

from .util import hsv_to_rgb, rgb_to_hsv


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


class TPLinkPlugProperty(TPLinkProperty):
    """Property type for TP-Link smart plugs."""

    def set_value(self, value):
        """
        Set the current value of the property.

        value -- the value to set
        """
        try:
            if self.name == 'on':
                self.device.hs100_dev.state = 'ON' if value else 'OFF'
            elif self.name == 'led-on':
                self.device.hs100_dev.led = value
            elif self.name == 'level':
                self.device.hs100_dev.brightness = value
            else:
                return
        except SmartDeviceException:
            return

        self.set_cached_value(value)
        self.device.notify_property_changed(self)

    def update(self, sysinfo, emeter):
        """
        Update the current value, if necessary.

        sysinfo -- current sysinfo dict for the device
        emeter -- current emeter for the device
        """
        if self.name == 'on':
            value = self.device.is_on(sysinfo)
        elif self.name == 'led-on':
            value = self.device.is_led_on(sysinfo)
        elif self.name == 'level':
            value = self.device.brightness(sysinfo)
        elif self.name == 'instantaneousPower':
            value = self.device.power(emeter)
        elif self.name == 'voltage':
            value = self.device.voltage(emeter)
        elif self.name == 'current':
            value = self.device.current(emeter)
        else:
            return

        if value != self.value:
            self.set_cached_value(value)
            self.device.notify_property_changed(self)


class TPLinkBulbProperty(TPLinkProperty):
    """Property type for TP-Link smart bulbs."""

    def set_value(self, value):
        """
        Set the current value of the property.

        value -- the value to set
        """
        color_mode_prop = None
        if 'colorMode' in self.device.properties:
            color_mode_prop = self.device.properties['colorMode']

        level_prop = None
        if 'level' in self.device.properties:
            level_prop = self.device.properties['level']

        try:
            if self.name == 'on':
                self.device.hs100_dev.state = 'ON' if value else 'OFF'
            elif self.name == 'color':
                hsv = rgb_to_hsv(value)
                self.device.hs100_dev.hsv = hsv

                # update the level property
                if level_prop is not None:
                    level_prop.set_cached_value(hsv[2])
                    self.device.notify_property_changed(level_prop)

                # update the colorMode property
                if color_mode_prop is not None:
                    color_mode_prop.set_cached_value('color')
                    self.device.notify_property_changed(color_mode_prop)
            elif self.name == 'level':
                self.device.hs100_dev.brightness = value
            elif self.name == 'colorTemperature':
                value = max(value, self.description['minimum'])
                value = min(value, self.description['maximum'])
                self.device.hs100_dev.color_temp = int(value)

                # update the colorMode property
                if color_mode_prop is not None:
                    color_mode_prop.set_cached_value('temperature')
                    self.device.notify_property_changed(color_mode_prop)
            else:
                return
        except SmartDeviceException:
            return

        self.set_cached_value(value)
        self.device.notify_property_changed(self)

    def update(self, sysinfo, light_state, emeter):
        """
        Update the current value, if necessary.

        sysinfo -- current sysinfo dict for the device
        light_state -- current state of the light
        emeter -- current emeter for the device
        """
        if self.name == 'on':
            value = self.device.is_on(light_state)
        elif self.name == 'color':
            value = hsv_to_rgb(*self.device.hsv(light_state))
        elif self.name == 'level':
            value = self.device.brightness(light_state)
        elif self.name == 'colorTemperature':
            value = self.device.color_temp(light_state)
        elif self.name == 'colorMode':
            value = self.device.color_mode(light_state)
        elif self.name == 'instantaneousPower':
            value = self.device.power(emeter)
        elif self.name == 'voltage':
            value = self.device.voltage(emeter)
        elif self.name == 'current':
            value = self.device.current(emeter)
        else:
            return

        if value != self.value:
            self.set_cached_value(value)
            self.device.notify_property_changed(self)
