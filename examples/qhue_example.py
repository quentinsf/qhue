#!/usr/bin/env python

from os import path
from qhue import Bridge, QhueException, create_new_username

# the IP address of your bridge
BRIDGE_IP = "192.168.0.45"

# the path for the username credentials file
CRED_FILE_PATH = "qhue_username.txt"

def main():

    # check for a credential file
    if not path.exists(CRED_FILE_PATH):

        while True:
            try:
                username = create_new_username(BRIDGE_IP)
                break
            except QhueException as err:
                print("Error occurred while creating a new username: {}".format(err))

        # store the username in a credential file
        with open(CRED_FILE_PATH, "w") as cred_file:
            cred_file.write(username)

    else:
        with open(CRED_FILE_PATH, "r") as cred_file:
            username = cred_file.read()

    # create the bridge resource, passing the captured username
    bridge = Bridge(BRIDGE_IP, username)

    # create a lights resource
    lights = bridge.lights

    # query the API and print the results
    print(lights())

if __name__ == "__main__":
    main()
