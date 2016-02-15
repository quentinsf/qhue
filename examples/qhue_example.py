# load dependency for path.exists()
from os import path

# load dependency for Bridge()
from qhue.qhue import Bridge

# load dependency for exc_info()
from sys import exc_info

# check for a credential file
if not path.exists("qhue_username.txt"):
  # create a bridge resource
  b = Bridge("192.168.0.45")

  # try connecting anonymously to the bridge
  try:
    username = b(devicetype="testdev", http_method="post")[0]["success"]["username"]
  # catch the error which is raised and print its message
  except:
    print(exc_info()[1])

  # press the bridge button
  raw_input("Press Return after pressing the bridge button")

  # connect anonymously to the bridge again, to create an user
  username = b(devicetype="testdev", http_method="post")[0]["success"]["username"]

  # store the username in a credential file
  file = open("qhue_username.txt", "w")
  file.write(username)
  file.close()
else:
  file = open("qhue_username.txt", "r")
  username = file.read()
  file.close()

# (re)create the bridge resource, passing the captured username
b = Bridge("192.168.0.45", username)

# create a lights resource
lights = b.lights

# query the API and print the results
print lights()
