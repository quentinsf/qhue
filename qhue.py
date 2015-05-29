# Qhue is (c) Quentin Stafford-Fraser 2014
# but distributed under the GPL v2.

import requests
import json

class QhueException(Exception):
    pass

class Resource(object):
    def __init__(self, url, timeout=5):
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
        return Resource(self.url + "/" + str(name))

    __getitem__ = __getattr__
    

class Bridge(Resource):
    def __init__(self, ip, username=None, timeout=5):
        self.ip = ip
        self.username = username
        url = "http://{i}/api".format(i = self.ip)
        if username: 
            url += "/{u}".format(u=username)
        super(Bridge, self).__init__(url, timeout=timeout)
