
# See http://wiki.micasaverde.com/index.php/Luup_Requests

import requests, json

from hub import BaseDevice, DeviceException

   
class Device(BaseDevice):

    def configure(self, **config):
        super().configure(**config)
        self.address = config.get('address')
        if self.address is None:
            raise DeviceException('Address is required!')
        self.port = config.get('port', 3480)
        self.timeout = config.get('timeout', 2)
        self.__reset()
        self.requestURL = 'http://{}:{}/data_request'.format(self.address, self.port)

    def start(self):
        if self.connected: return
        super().start()

        try:
            data = self.__request(id = 'sdata')
            self.logger.info('Model: {}'.format(data['model']))
            self.logger.info('Serial #: {}'.format(data['serial_number']))
            
            self.devices = data['devices']
            self.categories = data['categories']
            self.scenes = data['scenes']
            self.rooms = data['rooms']

            self.logger.info('Available devices: {}'.format(', '.join(['{} ({})'.format(d['name'], d['id']) for d in self.devices])))
            self.logger.info('Available categories: {}'.format(', '.join(['{} ({})'.format(c['name'], c['id']) for c in self.categories])))
            self.logger.info('Available scenes: {}'.format(', '.join(['{} ({})'.format(s['name'], s['id']) for s in self.scenes])))
            
            self.logger.info('Connected to VeraEdge at {}:{}'.format(self.address, self.port))
            self.connected = True
       
        except:
            self.logger.exception('Unable to connect to {}:{}:'.format(self.address, self.port))
       
    def stop(self):
        if not self.connected: return
        super().stop()
        self.logger.info('Disconnected from VeraEdge at {}:{}'.format(self.address, self.port))
        self.__reset()

    def __reset(self):
        self.connected = False
        self.requestURL = None

    def __request(self, **params):
        params['output_format'] = 'json'
        res = requests.get(url = self.requestURL, params = params, timeout = self.timeout)
        return res.json()

    def __getDevice(self, idOrName):
        d = next((d for d in self.devices if d['id'] == idOrName or d['name'] == idOrName), None)
        if d is None:
            raise DeviceException('Device "{}" not found!'.format(idOrName))
        return d
        
    def __getCategory(self, idOrName):
        c = next((c for c in self.categories if c['id'] == idOrName or c['name'] == idOrName), None)
        if c is None:
            raise DeviceException('Category "{}" not found!'.format(idOrName))
        return c
    
    def __getScene(self, idOrName):
        s = next((s for s in self.scenes if s['id'] == idOrName or s['name'] == idOrName), None)
        if s is None:
            raise DeviceException('Scene "{}" not found!'.format(idOrName))
        return s
    
    #--------------------------------------------------------------------------
    # Public API
    #

    def turnOnSwitch(self, deviceIdOrName):
        if not self.connected: return
        d = self.__getDevice(deviceIdOrName)
        self.logger.info('Turning on switch "{}"'.format(d['name']))
        self.__request(id = 'action',
                       DeviceNum = d['id'],
                       serviceId = 'urn:upnp-org:serviceId:SwitchPower1',
                       action = 'SetTarget',
                       newTargetValue = 1)
        
    def turnOffSwitch(self, deviceIdOrName):
        if not self.connected: return
        d = self.__getDevice(deviceIdOrName)
        self.logger.info('Turning off switch "{}"'.format(d['name']))
        self.__request(id = 'action',
                       DeviceNum = d['id'],
                       serviceId = 'urn:upnp-org:serviceId:SwitchPower1',
                       action = 'SetTarget',
                       newTargetValue = 0)
    
    # virtual category 999 for all lights
    def turnOnSwitches(self, categoryIdOrName):
        if not self.connected: return
        c = self.__getCategory(categoryIdOrName)
        self.logger.info('Turning on switches in category "{}"'.format(c['name']))
        self.__request(id = 'action',
                       Category = c['id'],
                       serviceId = 'urn:upnp-org:serviceId:SwitchPower1',
                       action = 'SetTarget',
                       newTargetValue = 1)
    
    def turnOffSwitches(self, categoryIdOrName):
        if not self.connected: return
        c = self.__getCategory(categoryIdOrName)
        self.logger.info('Turning off switches in category "{}"'.format(c['name']))
        self.__request(id = 'action',
                       Category = c['id'],
                       serviceId = 'urn:upnp-org:serviceId:SwitchPower1',
                       action = 'SetTarget',
                       newTargetValue = 0)
    
    def dimLight(self, deviceIdOrName, percent):
        if not self.connected: return
        d = self.__getDevice(deviceIdOrName)
        percent = int(percent) if percent > 1 else int(percent * 100)
        self.logger.info('Dimming light "{}"'.format(d['name']))
        self.__request(id = 'action',
                       DeviceNum = d['id'],
                       serviceId = 'urn:upnp-org:serviceId:Dimming1',
                       action = 'SetLoadLevelTarget',
                       newLoadlevelTarget = percent)

    def dimLights(self, categoryIdOrName, percent):
        if not self.connected: return
        c = self.__getCategory(categoryIdOrName)
        percent = int(percent) if percent > 1 else int(percent * 100)
        self.logger.info('Dimming lights in category "{}"'.format(c['name']))
        self.__request(id = 'action',
                       Category = c['id'],
                       serviceId = 'urn:upnp-org:serviceId:Dimming1',
                       action = 'SetLoadLevelTarget',
                       newLoadlevelTarget = percent)
    
    def runScene(self, sceneIdOrName):
        if not self.connected: return
        s = self.__getScene(sceneIdOrName)
        self.logger.info('Running scene "{}"'.format(s['name']))
        self.__request(id = 'action',
                       serviceId = 'urn:micasaverde-com:serviceId:HomeAutomationGateway1',
                       action = 'RunScene',
                       SceneNum = s['id'])
