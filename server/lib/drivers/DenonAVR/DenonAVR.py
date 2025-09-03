#
# https://github.com/ol-iver/denonavr
#

import asyncio
import denonavr
from hub import BaseDevice, DeviceException

   
class Device(BaseDevice):

    def configure(self, **config):
        super().configure(**config)
        self.address = config.get('address')
        if self.address is None:
            raise DeviceException('Address is required!')
        self.show_all_inputs = config.get('show_all_inputs', False)
        self.timeout = config.get('timeout', 2)
        self.__reset()

    def start(self):
        if self.connected: return
        super().start()

        self.avr = denonavr.DenonAVR(host = self.address, show_all_inputs = self.show_all_inputs, timeout = self.timeout)
        try:
            asyncio.run(self.avr.async_setup())
            asyncio.run(self.avr.async_update())
            self.logger.info('Connected to {} at {}'.format(self.avr.name, self.address))
            self.connected = True
            
            self.logger.info('Available inputs: ' + ', '.join(self.avr.input_func_list))
            self.logger.info('Current input: ' + self.avr.input_func)
            self.logger.info('Available sound modes: ' + ', '.join(self.avr.sound_mode_list))
            self.logger.info('Current sound mode: ' + self.avr.sound_mode)
            self.soundMode = self.avr.sound_mode
        except:
            self.logger.exception('Unable to connect to {}'.format(self.address))
       
    def stop(self):
        if not self.connected: return
        super().stop()
        self.logger.info('Disconnected from {} at {}:{}'.format(self.avr.name, self.address))
        self.__reset()

    def __reset(self):
        self.connected = False
        self.avr = False

    #--------------------------------------------------------------------------
    # Public API
    #

    def powerOn(self):
        if not self.connected: return
        self.logger.info('Power on')
        asyncio.run(self.avr.async_power_on())

    def powerOff(self):
        if not self.connected: return
        self.logger.info('Power off')
        asyncio.run(self.avr.async_power_off())
        
    def volumeToggleMute(self):
        if not self.connected: return
        if self.avr.muted:
            self.volumeMuteOff()
        else:
            self.volumeMuteOn()
    
    def volumeMuteOn(self):
        if not self.connected: return
        self.logger.info('Mute on')
        asyncio.run(self.avr.async_mute(True))
        asyncio.run(self.avr.async_update())
    
    def volumeMuteOff(self):
        if not self.connected: return
        self.logger.info('Mute off')
        asyncio.run(self.avr.async_mute(False))
        asyncio.run(self.avr.async_update())
        
    def volumeUp(self):
        if not self.connected: return
        self.logger.info('Volume up')
        asyncio.run(self.avr.async_volume_up())
        
    def volumeDown(self):
        if not self.connected: return
        self.logger.info('Volume down')
        asyncio.run(self.avr.async_volume_down())

    def volumeSet(self, db = -25.0):
        if not self.connected: return
        self.logger.info('Set volume to {}'.format(db))
        asyncio.run(self.avr.async_set_volume(db))

    def sceneSelect(self, sceneNum):
        if not self.connected: return
        self.logger.info('Select scene {}'.format(sceneNum))
        # TODO

    def inputSelect(self, input):
        if not self.connected: return
        self.logger.info('Select input {}'.format(input))
        asyncio.run(self.avr.async_set_input_func(input))
        #asyncio.run(self.avr.update())
        
    def soundModeSelect(self, soundMode):
        if not self.connected: return
        self.logger.info('Select sound mode {}'.format(soundMode))
        asyncio.run(self.avr.async_set_sound_mode(soundMode))
        self.soundMode = soundMode
        #asyncio.run(self.avr.update())
        
