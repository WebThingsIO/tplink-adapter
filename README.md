# tplink-adapter

TP-Link smart plug/bulb adapter for Mozilla IoT Gateway.

# Supported Devices

## Tested and Working

* Smart plugs
    * HS105
    * HS110
* Smart bulbs
    * LB110
    * LB120
    * LB130
* Smart switches
    * HS200

## Untested but _Should Work_

* Smart plugs
    * HS100
    * HS103
* Smart bulbs
    * LB100
    * LB200
    * LB230
* Smart switches
    * HS210
    * HS220

# Unsupported Devices

There's nothing technically preventing support for these devices, they just have not been tested at all.

* WiFi range extenders + smart plug
    * RE270K
    * RE370K

# Requirements

If you're running this add-on outside of the official gateway image for the Raspberry Pi, i.e. you're running on a development machine, you'll need to do the following (adapt as necessary for non-Ubuntu/Debian):

```
sudo apt install python3-dev libnanomsg-dev
sudo pip3 install nnpy
sudo pip3 install git+https://github.com/mozilla-iot/gateway-addon-python.git
```
