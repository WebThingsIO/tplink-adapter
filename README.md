# tplink-adapter

TP-Link Kasa smart plug/bulb adapter for WebThings Gateway.

# Supported Devices

## Tested and Working

* Smart plugs
    * HS100
    * HS103
    * HS105
    * HS107
    * HS110
    * HS300
* Smart bulbs
    * LB110
    * LB120
    * LB130
* Smart switches
    * HS200
    * HS210

## Untested but _Should Work_

* Smart plugs
    * KP100
* Smart bulbs
    * LB100
    * LB200
    * LB230
    * KB100
    * KB130
    * KL110
    * KL120
    * KL130
* Smart switches
    * HS220

# Unsupported Devices

## Kasa

There's nothing technically preventing support for these devices, they just have not been tested at all.

* WiFi range extenders + smart plug
* Cameras
* Video door bells

## Tapo

TP-Link Tapo devices will **NOT** work, as they use an entirely different protocol.

# Requirements

If you're running this add-on outside of the official gateway image for the Raspberry Pi, i.e. you're running on a development machine, you'll need to do the following (adapt as necessary for non-Ubuntu/Debian):

```
sudo pip3 install git+https://github.com/WebThingsIO/gateway-addon-python.git
```
