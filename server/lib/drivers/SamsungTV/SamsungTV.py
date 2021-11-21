
#
# See https://github.com/openhab/openhab1-addons/tree/master/bundles/binding/org.openhab.binding.samsungtv for more keys
#

from samsungtv import SamsungTV
from hub import BaseDevice, DeviceException
   
class Device(BaseDevice):

    def configure(self, **config):
        super().configure(**config)
        self.address = config.get('address')
        if self.address is None:
            raise DeviceException('Address is required!')
        self.port = config.get('port', 8001)
        self.__reset()

    def start(self):
        if self.connected: return
        super().start()

        try:
            self.__tv = SamsungTV(self.address, self.port, name = 'RCHub')
            
            self.logger.info('Connected to {}:{}'.format(self.address, self.port))
            self.connected = True
       
        except:
            self.logger.exception('Unable to connect to {}:{}:'.format(self.address, self.port))
       
    def stop(self):
        if not self.connected: return
        super().stop()
        self.__tv.close()
        self.logger.info('Disconnected from {}:{}'.format(self.address, self.port))
        self.__reset()

    def __reset(self):
        self.connected = False
        self.__tv = None


    #--------------------------------------------------------------------------
    # Public API
    #

    def powerToggle(self):
        if not self.connected: return
        self.logger.info('Power toggle')
        self.__tv.send_key('KEY_POWER')

    def powerOn(self):
        if not self.connected: return
        self.logger.info('Power on')
        self.__tv.send_key('KEY_POWERON')

    def powerOff(self):
        if not self.connected: return
        self.logger.info('Power off')
        self.__tv.send_key('KEY_POWEROFF')

    def home(self):
        if not self.connected: return
        self.logger.info('Home')
        self.__tv.send_key('KEY_HOME')

    def menu(self):
        if not self.connected: return
        self.logger.info('Menu')
        self.__tv.send_key('KEY_MENU')

    def source(self):
        if not self.connected: return
        self.logger.info('Source')
        self.__tv.send_key('KEY_SOURCE')

    def guide(self):
        if not self.connected: return
        self.logger.info('Guide')
        self.__tv.send_key('KEY_GUIDE')

    def tools(self):
        if not self.connected: return
        self.logger.info('Tools')
        self.__tv.send_key('KEY_TOOLS')

    def info(self):
        if not self.connected: return
        self.logger.info('Info')
        self.__tv.send_key('KEY_INFO')

    def up(self):
        if not self.connected: return
        self.logger.info('Up')
        self.__tv.send_key('KEY_UP')

    def down(self):
        if not self.connected: return
        self.logger.info('Down')
        self.__tv.send_key('KEY_DOWN')

    def left(self):
        if not self.connected: return
        self.logger.info('Left')
        self.__tv.send_key('KEY_LEFT')

    def right(self):
        if not self.connected: return
        self.logger.info('Right')
        self.__tv.send_key('KEY_RIGHT')

    def enter(self):
        if not self.connected: return
        self.logger.info('Enter')
        self.__tv.send_key('KEY_ENTER')

    def back(self):
        if not self.connected: return
        self.logger.info('Back')
        self.__tv.send_key('KEY_RETURN')

    def exit(self):
        if not self.connected: return
        self.logger.info('Exit')
        self.__tv.send_key('KEY_EXIT')

    def channelList(self):
        if not self.connected: return
        self.logger.info('Channel list')
        self.__tv.send_key('KEY_CH_LIST')    

    def channel(self, ch):
        if not self.connected: return
        self.logger.info('Channel {}'.format(ch))
        self.__tv.channel(ch)

    def digit(self, d):
        if not self.connected: return
        self.logger.info('Digit {}'.format(d))
        self.__tv.send_key('KEY_' + d)

    def channelUp(self):
        if not self.connected: return
        self.logger.info('Channel up')
        self.__tv.send_key('KEY_CHUP')

    def channelDown(self):
        if not self.connected: return
        self.logger.info('Channel down')
        self.__tv.send_key('KEY_CHDOWN')

    def volumeUp(self):
        if not self.connected: return
        self.logger.info('Volume up')
        self.__tv.send_key('KEY_VOLUP')

    def volumeDown(self):
        if not self.connected: return
        self.logger.info('Volume down')
        self.__tv.send_key('KEY_VOLDOWN')

    def volumeMute(self):
        if not self.connected: return
        self.logger.info('Volume mute')
        self.__tv.send_key('KEY_MUTE')

    def play(self):
        if not self.connected: return
        self.logger.info('Play')
        self.__tv.send_key('KEY_PLAY')

    def pause(self):
        if not self.connected: return
        self.logger.info('Pause')
        self.__tv.send_key('KEY_PAUSE')

    def rewind(self):
        if not self.connected: return
        self.logger.info('Rewind')
        self.__tv.send_key('KEY_REWIND')

    def forward(self):
        if not self.connected: return
        self.logger.info('Forward')
        self.__tv.send_key('KEY_FF')
        
    def red(self):
        if not self.connected: return
        self.logger.info('Red')
        self.__tv.send_key('KEY_RED')

    def green(self):
        if not self.connected: return
        self.logger.info('Green')
        self.__tv.send_key('KEY_GREEN')

    def yellow(self):
        if not self.connected: return
        self.logger.info('Yellow')
        self.__tv.send_key('KEY_YELLOW')

    def blue(self):
        if not self.connected: return
        self.logger.info('Blue')
        self.__tv.send_key('KEY_BLUE')