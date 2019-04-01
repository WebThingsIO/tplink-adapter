# tplink-adapter

TP-Link smart plug/bulb adapter for Mozilla WebThings Gateway.

# Supported Devices

## Tested and Working

* Smart plugs
    * HS100
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
    * HS103
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

There's nothing technically preventing support for these devices, they just have not been tested at all.

* WiFi range extenders + smart plug
* Cameras
* Video door bells

# Requirements

If you're running this add-on outside of the official gateway image for the Raspberry Pi, i.e. you're running on a development machine, you'll need to do the following (adapt as necessary for non-Ubuntu/Debian):

```
sudo apt install python3-dev libnanomsg-dev
sudo pip3 install nnpy
sudo pip3 install git+https://github.com/mozilla-iot/gateway-addon-python.git
```
