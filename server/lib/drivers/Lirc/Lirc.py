
# See http://www.lirc.org/api-docs/html/group__python__bindings.html

import lirc, time

from hub import BaseDevice, DeviceException


class RemoteKey():

    def __init__(self, device, key):
        self.device = device
        self.name = key
        
    def down(self):
        self.device.keyDown(key)
        
    def up(self):
        self.device.keyUp(key)
        
    def press(self, downTime = None):
        self.device.keyPress(key, downTime)
        
        
class Device(BaseDevice):

    def configure(self, **config):
        super().configure(**config)
        self.socket = config.get('socket', lirc.client.get_default_socket_path())
        self.remote = config.get('remote')
        if self.remote is None:
            raise DeviceException('Remote name is required!')
        self.buttonMap = config.get('buttonMap', {})
        self.keyPressDownTime = config.get('keyPressDownTime', 0.25)
        if self.keyPressDownTime <= 0:
            raise DeviceException('keyPressDownTime must be positive!')
        self.__reset()

    def start(self):
        if self.__lirc is not None: return
        super().start()

        try:
            self.__lirc = lirc.CommandConnection(socket_path = self.socket)
        
            reply = lirc.VersionCommand(self.__lirc).run()
            version = reply.data[0]
            
            reply = lirc.ListRemotesCommand(self.__lirc).run()
            if self.remote not in reply.data:
                raise DeviceException('Remote "{}" is not in the list of available remotes: {}'.format(self.remote, ', '.join(reply.data)))

            self.__keys = {}
            reply = lirc.ListKeysCommand(self.__lirc, self.remote).run()
            keys = [k.split()[1] for k in reply.data]
            for (button, key) in self.buttonMap.items():
                if key not in keys:
                    raise DeviceException('Remote key "{}" is not in the list of available keys for remote "{}": {}'.format(key, self.remote, ', '.join(keys)))
                key = RemoteKey(self, key)
                self.__keys[button] = key
                    
            self.logger.info('Connected to LIRC v{} at {}'.format(version, self.socket))
        
        except DeviceException:
            raise
        except:
            self.logger.exception('Unable to connect to LIRC at {}!'.format(self.socket))
            self.__reset()
        
    def stop(self):
        if self.__lirc is None: return
        super().stop()
        self.__lirc.close()
        self.logger.info('Disconnected from LIRC at {}'.format(self.socket))
        self.__reset()

    def __reset(self):
        self.__lirc = None
        self.__keys = None
        
    def __getKey(self, button):
        if button in self.__keys:
            return self.__keys[button]
        raise DeviceException('Unknown button "{}" for LIRC remote "{}"!'.format(button, self.remote))
        
    def __getattr__(self, attr):
        return self.__getKey(attr)
            
            
    #--------------------------------------------------------------------------
    # Public API
    #

    def keyDown(self, key):
        if self.__lirc is None: return
        self.logger.debug('Send key down for LIRC remote "{}" key "{}"'.format(self.remote, key))
        reply = lirc.StartRepeatCommand(self.__lirc, self.remote, key).run()
        if not reply.success:
            self.logger.error('Unable to start repeat for LIRC remote "{}", key "{}": {}'.format(self.remote, key, reply.data[0]))
        
    def keyUp(self, key):
        if self.__lirc is None: return
        self.logger.debug('Send key up for LIRC remote "{}" key "{}"'.format(self.remote, key))
        reply = lirc.StopRepeatCommand(self.__lirc, self.remote, key).run()
        if not reply.success:
            self.logger.error('Unable to stop repeat for LIRC remote "{}", key "{}": {}'.format(self.remote, key, reply.data[0]))
    
    # this doesn't work because of a bug in the LIRC python bindings as of [at least] LIRC v0.10.1
#    def keyPress(self, key):
#        if self.__lirc is None: return
#        reply = lirc.SendCommand(self.__lirc, self.remote, key).run()
#        if not reply.success:
#            self.logger.error('Unable to send command for LIRC remote "{}", key "{}": {}'.format(self.remote, key, reply.data[0]))
 
    # emulated version
    def keyPress(self, key, downTime = None):
        if self.__lirc is None: return
        if downTime is None:
            downTime = self.keyPressDownTime
        elif downTime <= 0:
            raise DeviceException('downTime must be positive!')
            
        self.logger.debug('Send key press for LIRC remote "{}" key "{}"'.format(self.remote, key))
        
        reply = lirc.StartRepeatCommand(self.__lirc, self.remote, key).run()
        if not reply.success:
            self.logger.error('Unable to press key for LIRC remote "{}", key "{}": {}'.format(self.remote, key, reply.data[0]))
            
        time.sleep(downTime)
        
        reply = lirc.StopRepeatCommand(self.__lirc, self.remote, key).run()
        if not reply.success:
            self.logger.error('Unable to release key for LIRC remote "{}", key "{}": {}'.format(self.remote, key, reply.data[0]))
                
