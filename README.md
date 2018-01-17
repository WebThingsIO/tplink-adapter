# tplink-adapter

TP-Link smart plug/bulb adapter for Mozilla IoT Gateway.

# Supported Devices

## Tested and Working

* Smart plugs
    * HS105 (HW version 1.0)
        * Represented as `onOffSwitch`
    * HS110 (HW version 1.0)
        * Represented as `smartPlug`
* Smart bulbs
    * LB110 (HW version 2.0)
        * Represented as `onOffLight`
    * LB120 (HW version 1.0)
        * Represented as `dimmableLight`
    * LB130 (HW version 1.0)
        * Represented as `dimmableColorLight`
* Smart switches
    * HS200 (HW version 2.0)
        * Represented as `onOffSwitch`

## Untested but _Should Work_

* Smart plugs
    * HS100 (all HW versions)
    * HS105 (all other HW versions)
    * HS110 (all other HW versions)
* Smart bulbs
    * LB100 (all HW versions)
    * LB110 (all other HW versions)
    * LB120 (all other HW versions)
    * LB130 (all other HW versions)
    * LB200 (all HW versions)
    * LB230 (all HW versions)

# Unsupported Devices

There's nothing technically preventing support for these devices, they just have not been tested at all and/or do not have corresponding Web Thing types.

* Smart switches
    * HS210
* Cameras
    * KC120
* WiFi range extenders + smart plug
    * RE270K
    * RE370K
