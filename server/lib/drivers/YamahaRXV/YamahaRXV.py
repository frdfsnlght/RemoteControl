#
# Inspiration for this was taken from: https://github.com/BirdAPI/yamaha-network-receivers
#

import http.client
from xml.dom import minidom
from hub import BaseDevice, DeviceException

   
REMOTE_CODES = {

    'Up':           '7A859D62',
    'Down':         '7A859C63',
    'Left':         '7A859F60',
    'Right':        '7A859E61',
    'Enter':        '7A85DE21',
    'Return':       '7A85AA55',
    'Level':        '7A858679',
    'On Screen':    '7A85847B',
    'Option':       '7A856B14',
    'Top Menu':     '7A85A0DF',
    'Pop Up Menu':  '7A85A4DB',

    '1':            '7F0151AE',
    '2':            '7F0152AD',
    '3':            '7F0153AC',
    '4':            '7F0154AB',
    '5':            '7F0155AA',
    '6':            '7F0156A9',
    '7':            '7F0157A8',
    '8':            '7F0158A7',
    '9':            '7F0159A6',
    '0':            '7F015AA5',
    '+10':          '7F015BA4',
    'ENT':          '7F015CA3',

    'Play':         '7F016897',
    'Stop':         '7F016996',
    'Pause':        '7F016798',
    'Search-':      '7F016A95',
    'Search+':      '7F016E94',
    'Skip-':        '7F016C93',
    'Skip+':        '7F016D92',
    'FM':           '7F015827',
    'AM':           '7F01552A'

}

class Device(BaseDevice):

    def configure(self, **config):
        self.address = config.get('address')
        if self.address is None:
            raise DeviceException('Address is required!')
        self.port = config.get('port', 80)
        self.timeout = config.get('timeout', 2)
        self.__reset()

    def start(self):
        if self.connected: return
        super().start()

        # attempt to connect to the receiver and discover it's capabilities
        try:
            doc = self.__getConfig()
            self.model = doc.getElementsByTagName('Model_Name')[0].firstChild.data
            
            for feature in doc.getElementsByTagName('Feature_Existence')[0].childNodes:
                if feature.firstChild.data != '0':
                    self.features.append(str(feature.tagName))
                    if 'Zone' in feature.tagName:
                        self.zones.append(str(feature.tagName))

            for input in doc.getElementsByTagName('Input')[0].childNodes:
                realName = str(input.tagName).replace('_', '')
                self.inputs.append(realName)
                self.inputNames[str(input.firstChild.data)] = realName
                
            self.logger.info('Connected to {} at {}:{}'.format(self.model, self.address, self.port))
            self.connected = True
       
        except:
            self.logger.exception('Unable to connect to {}:{}:'.format(self.address, self.port))
       
    def stop(self):
        if not self.connected: return
        super().stop()
        self.logger.info('Disconnected from {} at {}:{}'.format(self.model, self.address, self.port))
        self.__reset()

    def __reset(self):
        self.connected = False
        self.features = []
        self.zones = []
        self.inputs = []
        self.inputNames = {}
        self.defaultZone = 'Main_Zone'

    def __sendXML(self, reqXML):
        conn = http.client.HTTPConnection('{0}:{1}'.format(self.address, self.port), timeout = self.timeout)
        conn.request('POST', '/YamahaRemoteControl/ctrl', '', {'Content-type': 'text/xml'})
        conn.send(reqXML.encode('utf-8'))
        resXML = conn.getresponse().read().decode('utf-8')
        conn.close()
        doc = minidom.parseString(resXML)
        rc = int(doc.getElementsByTagName('YAMAHA_AV')[0].getAttribute('RC'))
        if rc != 0:
            self.logger.error('Non-zero result code {} from request: {}'.format(rc, reqXML))

            raise Exception('Non-zero result code {} from request!'.format(rc))
        return doc

    def __getXML(self, xml):
        return self.__sendXML('<YAMAHA_AV cmd="GET">{}</YAMAHA_AV>'.format(xml))

    def __putXML(self, xml):
        return self.__sendXML('<YAMAHA_AV cmd="PUT">{}</YAMAHA_AV>'.format(xml))
        
    def __putZoneXML(self, zone, xml):
        return self.__putXML('<{0}>{1}</{0}>'.format(zone, xml))

    def __getZoneXML(self, zone, xml):
        return self.__getXML('<{0}>{1}</{0}>'.format(zone, xml))

    def __getConfig(self):
        return self.__getXML('<System><Config>GetParam</Config></System>')

    def __getZoneStatus(self, zone = None):
        return self.__getZoneXML(zone, '<Basic_Status>GetParam</Basic_Status>')
    
    def __getCurrentZoneInput(self, zone):
        doc = self.__getZoneStatus(zone)
        return doc.getElementsByTagName('Input_Sel')[0].firstChild.data

    def __getZone(self, zone):
        return zone if zone is not None else self.defaultZone
        
    def __sendRemoteCode(self, code):
        self.__putXML('<System><Misc><Remote_Signal><Receive><Code>{}</Code></Receive></Remote_Signal></Misc></System>'.format(code))


    #--------------------------------------------------------------------------
    # Public API
    #

    def setDefaultZone(self, zone = 'Main_Zone'):
        if zone not in self.zones:
            raise Exception('Unknown zone: {}'.format(zone))
        self.logger.info('Default zone is now {}'.format(zone))
        self.defaultZone = zone
        
    def powerOn(self, zone = None):
        if not self.connected: return
        zone = self.__getZone(zone)
        self.logger.info('Power on for zone {}'.format(zone))
        self.__putZoneXML(zone, '<Power_Control><Power>On</Power></Power_Control>')

    def powerOff(self, zone = None):
        if not self.connected: return
        zone = self.__getZone(zone)
        self.logger.info('Power off for zone {}'.format(zone))
        self.__putZoneXML(zone, '<Power_Control><Power>Off</Power></Power_Control>')
        
    def powerStandby(self, zone = None):
        if not self.connected: return
        zone = self.__getZone(zone)
        self.logger.info('Power standby for zone {}'.format(zone))
        self.__putZoneXML(zone, '<Power_Control><Power>Standby</Power></Power_Control>')
        
    def volumeToggleMute(self, zone = None):
        if not self.connected: return
        zone = self.__getZone(zone)
        doc = self.__getZoneStatus(zone)
        status = doc.getElementsByTagName('Mute')[0].firstChild.data
        if status == 'On':
            self.volumeMuteOff(zone)
        elif status == 'Off':
            self.volumeMuteOn(zone)
    
    def volumeMuteOn(self, zone = None):
        if not self.connected: return
        zone = self.__getZone(zone)
        self.logger.info('Mute zone {}'.format(zone))
        self.__putZoneXML(zone, '<Volume><Mute>On</Mute></Volume>')
    
    def volumeMuteOff(self, zone = None):
        if not self.connected: return
        zone = self.__getZone(zone)
        self.logger.info('Unmute zone {}'.format(zone))
        self.__putZoneXML(zone, '<Volume><Mute>Off</Mute></Volume>')
        
    def volumeUp(self, zone = None):
        if not self.connected: return
        zone = self.__getZone(zone)
        self.logger.info('Volume up for zone {}'.format(zone))
        self.__putZoneXML(zone, '<Volume><Lvl><Val>Up</Val><Exp></Exp><Unit></Unit></Lvl></Volume>')
        
    def volumeDown(self, zone = None):
        if not self.connected: return
        zone = self.__getZone(zone)
        self.logger.info('Volume down for zone {}'.format(zone))
        self.__putZoneXML(zone, '<Volume><Lvl><Val>Down</Val><Exp></Exp><Unit></Unit></Lvl></Volume>')

    def volumeSet(self, db = -25.0, zone = None):
        if not self.connected: return
        zone = self.__getZone(zone)
        self.logger.info('Set volume to {} for zone {}'.format(db, zone))
        self.__putZoneXML(zone, '<Volume><Lvl><Val>{}</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume>'.format(int(value * 10.0)))

    def sceneSelect(self, sceneNum, zone = None):
        if not self.connected: return
        zone = self.__getZone(zone)
        self.logger.info('Select scene {} for zone {}'.format(sceneNum, zone))
        self.__putZoneXML(zone, '<Scene><Scene_Sel>Scene {0}</Scene_Sel></Scene>'.format(int(sceneNum)))

    def inputSelect(self, input, zone = None):
        if not self.connected: return
        zone = self.__getZone(zone)
        self.logger.info('Select input {} for zone {}'.format(input, zone))
        # handle real or renamed source names
        if input in self.inputNames:
            input = self.inputNames[input]
        self.__putZoneXML(zone, '<Input><Input_Sel>{}</Input_Sel></Input>'.format(input))
        
    def inputNext(self, zone = None):
        if not self.connected: return
        zone = self.__getZone(zone)
        input = self.__getCurrentZoneInput(zone)
        index = self.inputs.index(input) if input in self.inputs else -1
        index = index + 1
        if index >= len(self.inputs):
            index = 0
        input = self.inputs[index]
        self.inputSelect(input, zone)

    def inputPrevious(self, zone = None):
        if not self.connected: return
        zone = self.__getZone(zone)
        input = self.__getCurrentZoneInput(zone)
        index = self.inputs.index(input) if input in self.inputs else len(self.inputs)
        index = index - 1
        if index < 0:
            index = len(self.inputs) - 1
        input = self.inputs[index]
        self.inputSelect(input, zone)

    def sendRemoteCode(self, codeKey):
        if not self.connected: return
        codeValue = REMOTE_CODES.get(codeKey, None)
        if codeValue is None:
            raise DeviceException('Invalid remote code {}!'.format(codeKey))
        self.logger.info('Send remote code {}'.format(codeKey))
        self.__sendRemoteCode(codeValue)

    