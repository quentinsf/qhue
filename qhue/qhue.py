# Qhue is (c) Quentin Stafford-Fraser 2017
# but distributed under the GPL v2.

import requests
import json
# for hostname retrieval for registering with the bridge
from socket import getfqdn
import re
import sys

__all__ = ('Bridge', 'QhueException', 'create_new_username')

# default timeout in seconds
_DEFAULT_TIMEOUT = 5


class Resource(object):
    def __init__(self, url, timeout=_DEFAULT_TIMEOUT, object_pairs_hook=None):
        self.url = url
        self.address = url[url.find('/api'):]
        # Also find the bit after the username, if there is one
        self.short_address = None
        post_username_match = re.search(r'/api/[^/]*(.*)', url)
        if post_username_match is not None:
            self.short_address = post_username_match.group(1)
        self.timeout = timeout
        self.object_pairs_hook = object_pairs_hook

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
        resp = r.json(object_pairs_hook=self.object_pairs_hook)
        if type(resp) == list:
            errors = [m['error']['description'] for m in resp if 'error' in m]
            if errors:
                raise QhueException("\n".join(errors))
        return resp

    def __getattr__(self, name):
        return Resource(self.url + "/" + str(name), timeout=self.timeout,
                object_pairs_hook=self.object_pairs_hook)

    __getitem__ = __getattr__


def _api_url(ip, username=None):
    if username is None:
        return "http://{}/api".format(ip)
    else:
        return "http://{}/api/{}".format(ip, username)


def create_new_username(ip, devicetype=None, timeout=_DEFAULT_TIMEOUT):
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
    res = Resource(_api_url(ip), timeout)
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


class Bridge(Resource):

    def __init__(self, ip, username, timeout=_DEFAULT_TIMEOUT, object_pairs_hook=None):
        """Create a new connection to a hue bridge.

        If a whitelisted username has not been generated yet, use
        create_new_username to have the bridge interactively generate
        a random username and then pass it to this function.

        Args:
            ip: ip address of the bridge
            username: valid username for the bridge
            timeout (optional, default=5): request timeout in seconds
            object_pairs_hook (optional): function called by JSON decoder with
                the result of any object literal as an ordered list of pairs.
        """
        self.ip = ip
        self.username = username
        url = _api_url(ip, username)
        super(Bridge, self).__init__(url, timeout=timeout, object_pairs_hook=object_pairs_hook)


class QhueException(Exception):
    pass
