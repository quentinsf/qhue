# Qhue is (c) Quentin Stafford-Fraser 2014
# but distributed under the GPL v2.

import requests
import json
# for hostname retrieval for registering with the bridge
from socket import getfqdn

__all__ = ('Bridge', 'QhueException', 'create_new_username')

# default timeout in seconds
_DEFAULT_TIMEOUT = 5


class Resource(object):
    def __init__(self, url, timeout=_DEFAULT_TIMEOUT):
        self.url = url
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
        resp = r.json()
        if type(resp)==list:
            errors = [m['error']['description'] for m in resp if 'error' in m]
            if errors:
                raise QhueException("\n".join(errors))
        return resp

    def __getattr__(self, name):
        return Resource(self.url + "/" + str(name), timeout=self.timeout)

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
    raw_input("Press the Bridge button, then press Return.")

    fq_device_type = "qhue@{}".format(getfqdn())

    # raises QhueException if something went wrong
    response = res(devicetype=fq_device_type, http_method="post")

    return response[0]["success"]["username"]


class Bridge(Resource):
    def __init__(self, ip, username, timeout=_DEFAULT_TIMEOUT):
        """Create a new connection to a hue bridge.

        If a whitelisted username has not been generated yet, first, use
        create_new_username to have the bridge interactively generate a random
        username and then construct.

        Args:
            ip: ip address of the bridge
            username: valid username for the bridge
            timeout (optional, default=5): request timeout in seconds
        """
        self.ip = ip
        self.username = username
        url = _api_url(ip, username)
        super(Bridge, self).__init__(url, timeout=timeout)


class QhueException(Exception):
    pass
