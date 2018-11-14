# Qhue is (c) Quentin Stafford-Fraser 2017
# but distributed under the GPL v2.

import collections
import requests
import json
# for hostname retrieval for registering with the bridge
from socket import getfqdn
import re
import sys
import os

__all__ = ('Bridge', 'QhueException')

# default timeout in seconds
_DEFAULT_TIMEOUT = 5


class Resource(object):

    def __init__(self, url, timeout=_DEFAULT_TIMEOUT):
        self.url = url
        self.address = url[url.find('/api'):]
        # Also find the bit after the username, if there is one
        self.short_address = None
        post_username_match = re.search(r'/api/[^/]*(.*)', url)
        if post_username_match is not None:
            self.short_address = post_username_match.group(1)
        self.timeout = timeout

    def __call__(self, *args, **kwargs):
        url = self.url
        for a in args:
            url += "/" + str(a)
        http_method = kwargs.pop('http_method',
            'get' if not kwargs else 'put').lower()
        if http_method == 'put':
            r = requests.put(url, data=json.dumps(kwargs, default=list), timeout=self.timeout)
        elif http_method == 'post':
            r = requests.post(url, data=json.dumps(kwargs, default=list), timeout=self.timeout)
        elif http_method == 'delete':
            r = requests.delete(url, timeout=self.timeout)
        else:
            r = requests.get(url, timeout=self.timeout)
        if r.status_code != 200:
            raise QhueException("Received response {c} from {u}".format(c=r.status_code, u=url))
        resp = r.json(object_pairs_hook=collections.OrderedDict)
        if type(resp) == list:
            errors = [m['error']['description'] for m in resp if 'error' in m]
            if errors:
                raise QhueException("\n".join(errors))
        return resp

    def __getattr__(self, name):
        return Resource(self.url + "/" + str(name), timeout=self.timeout)

    __getitem__ = __getattr__

class Bridge(Resource):

    def __init__(self, ip=None, username=None, timeout=_DEFAULT_TIMEOUT, configpath=os.path.expanduser('~/.config/qhue'), devicetype=None, newip=False, newuser=False):
        """Create a new connection to a hue bridge.

        If a whitelisted username has not been generated yet, use
        create_new_username to have the bridge interactively generate
        a random username and then pass it to this function.

        Args:
            ip: ip address of the bridge
            username: valid username for the bridge
            timeout (optional, default=5): request timeout in seconds
        """
        self.configpath = configpath
        if not ip:
            ip = self.read_ip_from_config(newip=newip)
        self.ip = ip

        if not username:
            username = self.read_username_from_config(newuser=newuser, devicetype=devicetype)
        self.username = username

        url = self._api_url(self.ip, username)
        super(Bridge, self).__init__(url, timeout=timeout)

    @staticmethod
    def _api_url(ip, username=None):
        if username is None:
            return "http://{}/api".format(ip)
        else:
            return "http://{}/api/{}".format(ip, username)

    @classmethod
    def create_new_username(cls, ip, devicetype=None, timeout=_DEFAULT_TIMEOUT):
        """Interactive helper function to generate a new anonymous username.

        Args:
            ip: ip address of the bridge
            devicetype (optional): devicetype to register with the bridge. If
                unprovided, generates a device type based on the local hostname.
            timeout (optional, default=5): request timeout in seconds
        Raises:
            QhueException if something went wrong with username generation (for
                example, if the bridge button wasn't pressed).
        """
        res = Resource(cls._api_url(ip), timeout)
        prompt = "Press the Bridge button, then press Return: "
        # Deal with one of the sillier python3 changes
        if sys.version_info.major == 2:
            _ = raw_input(prompt)
        else:
            _ = input(prompt)

        if devicetype is None:
            devicetype = "qhue#{}".format(getfqdn())

        # raises QhueException if something went wrong
        response = res(devicetype=devicetype, http_method="post")

        return response[0]["success"]["username"]

    def read_ip_from_config(self, newip=False):
        filepath = os.path.join(self.configpath, 'ip.conf')

        if newip or not os.path.exists(filepath):
            try:
                import discoverhue
            except ImportError:
                ip = input("Please enter the ip of the Hue bridge: ")
            else:
                print("Discovering Hue bridge, please wait...")
                bridge_id, ip = discoverhue.find_bridges().popitem()
                ip = ip.split('/')[2].split(':')[0]
                print("Found Hue bridge at ip", ip)

            # Create non existing config directory
            if not os.path.exists(self.configpath):
                os.makedirs(self.configpath)

            # Store the username in a credential file
            with open(filepath, "w") as ip_file:
                ip_file.write(ip)

        else:
            with open(filepath, "r") as ip_file:
                ip = ip_file.read()

        return ip

    def read_username_from_config(self, retries=3, newuser=False, devicetype=None):
        # Check for a credential file
        username = None
        filepath = os.path.join(self.configpath, 'username.conf')
        if newuser or not os.path.exists(filepath):
            for x in range(retries):
                try:
                    username = self.create_new_username(self.ip, devicetype=devicetype)
                    break
                except QhueException as err:
                    print("Error occurred while creating a new username: {}".format(err))

            if not username:
                raise QhueException("Failed to create new user ({} attempts).\n".format(retries))
            else:
                # Create non existing config directory
                if not os.path.exists(self.configpath):
                    os.makedirs(self.configpath)

                # Store the username in a credential file
                with open(filepath, "w") as cred_file:
                    cred_file.write(username)

        # Read existing credential file
        else:
            with open(filepath, "r") as cred_file:
                username = cred_file.read()

        return username


class QhueException(Exception):
    pass
