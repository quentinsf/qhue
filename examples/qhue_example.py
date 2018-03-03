#!/usr/bin/env python

from os import path
from qhue import Bridge, QhueException

# the IP address of your bridge
BRIDGE_IP = "192.168.0.45"

def main():
    # create the bridge resource, passing the captured username
    try:
        bridge = Bridge(BRIDGE_IP)
    except QhueException as err:
        sys.exit("Error occurred while creating Hue bridge object: {}".format(err))

    # create a lights resource
    lights = bridge.lights

    # query the API and print the results
    print(lights())

if __name__ == "__main__":
    main()
