#!/usr/bin/env python

from os import path
from qhue import Bridge, QhueException

def main():
    # create the bridge resource, passing the captured username
    try:
        bridge = Bridge()
    except QhueException as err:
        sys.exit("Error occurred while creating Hue bridge object: {}".format(err))

    # create a lights resource
    lights = bridge.lights

    # query the API and print the results
    print(lights())

if __name__ == "__main__":
    main()
