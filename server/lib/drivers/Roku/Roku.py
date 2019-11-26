
from roku import Roku

from hub import BaseDevice, DeviceException


class Device(BaseDevice):

    def configure(self, **config):
        super().configure(**config)
        self.address = config.get('address')
        self.discoveryTimeout = config.get('discoveryTimeout', 2)
        self.discoveryRetries = config.get('discoveryRetries', 2)
        self.__reset()

    def start(self):
        if self.connected: return
        super().start()

        # discover if no address is provided
        if self.address is None:
            rokus = Roku.discover(timeout = self.discoveryTimeout, retries = self.discoveryRetries)
            if len(rokus) == 0:
                self.logger.error('No Rokus found on the network!')
                return
            if len(rokus) > 1:
                self.logger.warning('More than one Roku was found on the network!')
            self.__roku = rokus[0]
        else:
            self.__roku = Roku(self.address)

        try:
        
            # get device info
            self.deviceInfo = self.__roku.device_info
        
            # get the available apps
            apps = self.__roku.apps
            self.logger.info('Available Roku apps: {}'.format(', '.join(['{} ({})'.format(app.name, app.id) for app in apps])))
        
            self.logger.info('Connected to {} at {}'.format(self.deviceInfo.model_name, self.__roku.host))
            self.connected = True
            
        except:
            self.logger.exception('Unable to connect to {}!'.format(self.__roku.host))
            self.__reset()
            
       
    def stop(self):
        if not self.connected: return
        super().stop()
        self.logger.info('Disconnected from {} at {}'.format(self.deviceInfo.model_name, self.__roku.host))
        self.__reset()

    def __reset(self):
        self.connected = False
        self.__roku = None
        self.deviceInfo = None
        
    
    #--------------------------------------------------------------------------
    # Public API
    #

    def up(self):
        if not self.connected: return
        self.__roku.up()
        
    def down(self):
        if not self.connected: return
        self.__roku.down()
        
    def left(self):
        if not self.connected: return
        self.__roku.left()
        
    def right(self):
        if not self.connected: return
        self.__roku.right()
        
    def select(self):
        if not self.connected: return
        self.__roku.select()
        
    def back(self):
        if not self.connected: return
        self.__roku.back()

    def forward(self):
        if not self.connected: return
        self.__roku.forward()
        
    def reverse(self):
        if not self.connected: return
        self.__roku.reverse()
        
    def play(self):
        if not self.connected: return
        self.__roku.play()
        
    def replay(self):
        if not self.connected: return
        self.__roku.replay()
        
    def backspace(self):
        if not self.connected: return
        self.__roku.backspace()
        
    def enter(self):
        if not self.connected: return
        self.__roku.enter()
        
    def home(self):
        if not self.connected: return
        self.__roku.home()
        
    def info(self):
        if not self.connected: return
        self.__roku.info()
        
    def literal(self, text):
        if not self.connected: return
        self.__roku.literal(text)
        
    def search(self):
        if not self.connected: return
        self.__roku.search()
        
    # will accept id or name
    def launchApp(self, appId):
        if not self.connected: return
        app = self.__roku[appId]
        if app is None:
            self.logger.error('No app with id or name "{}"!'.format(appId))
            return
        if self.__roku.active_app != app:
            self.logger.info('Launching app "{}"'.format(app.name))
            app.launch()
        