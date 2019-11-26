
# See /usr/share/kodi/system/keymaps/keyboard.xml for available keys

import os
from .xbmcclient import XBMCClient, PacketBUTTON

from hub import BaseDevice, DeviceException, Timer
   
class Device(BaseDevice):

    def configure(self, **config):
        super().configure(**config)
        self.address = config.get('address')
        if self.address is None:
            raise DeviceException('Address is required!')
        self.port = config.get('port', 9777)
        self.__reset()

    def start(self):
        if self.connected: return
        super().start()

        self.__defaultIcon = os.path.join(os.path.dirname(__file__), 'driver.png')
        self.kodi = XBMCClient('Slab Kodi Driver', self.__defaultIcon)
        self.kodi.connect(ip = self.address, port = self.port)
        
        self.__pingTimer = Timer(interval = 55, repeat = True, function = self.ping)
        self.__pingTimer.start()
        
        self.logger.info('Connected to Kodi at {}:{}'.format(self.address, self.port))
        self.connected = True
       
    def stop(self):
        if not self.connected: return
        super().stop()
        self.__pingTimer.cancel()
        self.kodi.close()
        self.logger.info('Disconnected from Kodi at {}:{}'.format(self.address, self.port))
        self.__reset()

    def __reset(self):
        self.connected = False
        self.kodi = None
        self.__pingTimer = None


    #--------------------------------------------------------------------------
    # Public API
    #

    def ping(self):
        if not self.connected: return
        self.kodi.ping()
        
    def notify(self, title, message, icon = None):
        if not self.connected: return
        if icon is None:
            icon = self.__defaultIcon
        self.kodi.send_notification(title, message, icon)
        self.__pingTimer.reset()
        
    def log(self, level = 0, message = ''):
        if not self.connected: return
        self.kodi.send_log(level, message)
        self.__pingTimer.reset()
        
    def keyPress(self, button):
        self.buttonPress('KB', button)
        
    def keyDown(self, button):
        self.buttonDown('KB', button)
        
    def keyUp(self, button):
        self.buttonUp('KB', button)
        
    def remotePress(self, button):
        self.buttonPress('R1', button)
        
    def remoteDown(self, button):
        self.buttonDown('R1', button)
        
    def remoteUp(self, button):
        self.buttonUp('R1', button)
        
    def buttonPress(self, keyMap, button):
        if not self.connected: return
        packet = PacketBUTTON(map_name = str(keyMap), button_name = str(button), down = 1, repeat = 0, queue = 0)
        packet.send(self.kodi.sock, self.kodi.addr, self.kodi.uid)
        self.__pingTimer.reset()
        
    def buttonDown(self, keyMap, button):
        if not self.connected: return
        self.kodi.send_button_state(map = keyMap, button = button, down = 1)
        self.__pingTimer.reset()
        
    def buttonUp(self, keyMap, button):
        if not self.connected: return
        self.kodi.send_button_state(map = keyMap, button = button, down = 0)
        self.__pingTimer.reset()
        
    def releaseAll(self):
        if not self.connected: return
        self.kodi.release_button()
        self.__pingTimer.reset()
        
    def action(self, action):
        if not self.connected: return
        self.kodi.send_action(action)
        self.__pingTimer.reset()
