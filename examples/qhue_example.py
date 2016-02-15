#!/usr/bin/env python

from os import path
from qhue import Bridge, QhueException

# the IP address of your bridge
BRIDGE_IP = "192.168.2.3"

# the path for the username credentials file
CRED_FILE_PATH = "qhue_username.txt"

def main():

    # check for a credential file
    if not path.exists(CRED_FILE_PATH):
        # create a bridge resource
        bridge = Bridge(BRIDGE_IP)

        while True:
            # press the bridge button
            raw_input("Press the bridge button, then press Return.")

            # connect anonymously to the bridge to create a user
            try:
                response = bridge(devicetype="testdev", http_method="post")
                username = response[0]["success"]["username"]
                break
            except QhueException as err:
                print "Error occurred while creating a new username: {}".format(err)

        # store the username in a credential file
        with open(CRED_FILE_PATH, "w") as cred_file:
            cred_file.write(username)

    else:
        with open(CRED_FILE_PATH, "r") as cred_file:
            username = cred_file.read()

    # (re)create the bridge resource, passing the captured username
    bridge = Bridge(BRIDGE_IP, username)

    # create a lights resource
    lights = bridge.lights

    # query the API and print the results
    print lights()

if __name__ == "__main__":
    main()
