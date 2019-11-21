
import requests, json

from hub import BaseDevice, DeviceException


class ClientRequest():

    def __init__(self, id, device):
        self.id = id
        self.device = device
        
    def configure(self, **config):
        self.url = config.get('url')
        if self.url is None:
            raise DeviceException('URL is required!')
        self.method = config.get('method', 'GET')
        self.timeout = config.get('timeout', 5)
        self.params = config.get('params', {})
        if not isinstance(self.params, dict):
            raise DeviceException('Params must be a dict!')
        self.data = config.get('data')
        if self.data is not None:
            if not isinstance(self.data, dict) and not isinstance(self.data, str):
                raise DeviceException('Data must be a dict or string!')
        self.headers = config.get('headers', {})
        if not isinstance(self.headers, dict):
            raise DeviceException('Headers must be a dict!')
        self.returnWhat = config.get('return')
        if self.returnWhat is not None and self.returnWhat.upper() not in ['STATUS', 'RESPONSE', 'JSON', 'TEXT', 'CONTENT']:
            raise DeviceException('Invalid return!')
        
    def request(self, **kwargs):
        url = self.url.format(**kwargs)
        method = self.method.format(**kwargs)
        params = {k:v.format(**kwargs) for (k, v) in self.params.items()}
        if isinstance(self.data, dict):
            data = {k:v.format(**kwargs) for (k, v) in self.data.items()}
        elif isinstance(self.data, str):
            data = self.data.format(**kwargs)
        headers = {k:v.format(**kwargs) for (k, v) in self.headers.items()}
        
        if self.method.upper() == 'GET':
            response = requests.get(url = url, params = params, headers = headers, timeout = self.timeout)
        elif self.method.upper() == 'POST':
            response = requests.post(url = url, params = params, data = data, headers = headers, timeout = self.timeout)
            
        if self.returnWhat is None:
            return
        if self.returnWhat.upper() == 'JSON':
            return response.json()
        if self.returnWhat.upper() == 'STATUS':
            return response.status_code
        if self.returnWhat.upper() == 'TEXT':
            return response.text
        if self.returnWhat.upper() == 'CONTENT':
            return response.content
        if self.returnWhat.upper() == 'RESPONSE':
            return response
        return None

   
class Device(BaseDevice):

    def configure(self, **config):
        self.__reset()
        self.requests = {}

        reqs = config.get('requests')
        if not isinstance(reqs, dict):
            raise DeviceException('No requests configured!')
            
        for (reqId, reqConf) in reqs.items():
            req = ClientRequest(reqId, self)
            req.configure(**reqConf)
            self.requests[req.id] = req

    def stop(self):
        super().stop()
        self.__reset()

    def __reset(self):
        self.requests = None

    #--------------------------------------------------------------------------
    # Public API
    #

    def request(self, requestId, **kwargs):
        req = self.requests.get(requestId)
        if req is None:
            raise DeviceException('Request "{}" is unknown!'.format(requestId))
        return req.request(**kwargs)
        