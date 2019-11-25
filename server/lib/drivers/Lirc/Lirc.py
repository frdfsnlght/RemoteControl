
# See http://www.lirc.org/api-docs/html/group__python__bindings.html

import lirc, time

from hub import BaseDevice, DeviceException


class Remote():

    def __init__(self, device, name):
        self.device = device
        self.name = name
        
    def keyDown(self, key):
        self.device.keyDown(self.name, key)
        
    def keyUp(self, key):
        self.device.keyUp(self.name, key)
        
    def keyPress(self, key):
        self.device.keyPress(self.name, key)
        
        
class Device(BaseDevice):

    def configure(self, **config):
        self.socket = config.get('socket', lirc.client.get_default_socket_path())
        self.remoteIds = config.get('remotes', {})
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
            self.logger.info('LIRC version {}'.format(reply.data[0]))
            
            reply = lirc.ListRemotesCommand(self.__lirc).run()
            self.logger.info('Available LIRC remotes: {}'.format(', '.join(reply.data)))
            
            for name in reply.data:
                remote = Remote(self, name)
                self.remotes[name] = remote
        
            for (id, name) in self.remoteIds.items():
                if name not in self.remotes:
                    self.logger.error('Remote "{}" ({}) is not a listed remote!'.format(id, name))
                    
            self.logger.info('Connected to LIRC at {}'.format(self.socket))
        
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
        self.remotes = {}
        
    def __getRemote(self, nameOrId):
        if nameOrId in self.remoteIds:
            nameOrId = self.remoteIds[nameOrId]
        if nameOrId in self.remotes:
            return self.remotes[nameOrId]
        raise DeviceException('Unknown LIRC remote "{}"!'.format(nameOrId))
        
    def __getattr__(self, attr):
        return self.__getRemote(attr)
            
            
    #--------------------------------------------------------------------------
    # Public API
    #

    def keyDown(self, remote, key):
        if self.__lirc is None: return
        self.logger.debug('Send key down for LIRC remote "{}" key "{}"'.format(remote, key))
        reply = lirc.StartRepeatCommand(self.__lirc, remote, key).run()
        if not reply.success:
            self.logger.error('Unable to start repeat for LIRC remote "{}", key "{}": {}'.format(remote, key, reply.data[0]))
        
    def keyUp(self, remote, key):
        if self.__lirc is None: return
        self.logger.debug('Send key up for LIRC remote "{}" key "{}"'.format(remote, key))
        reply = lirc.StopRepeatCommand(self.__lirc, remote, key).run()
        if not reply.success:
            self.logger.error('Unable to stop repeat for LIRC remote "{}", key "{}": {}'.format(remote, key, reply.data[0]))
    
    # this doesn't work because of a bug in the LIRC python bindings as of [at least] LIRC v0.10.1
#    def keyPress(self, remote, key):
#        if self.__lirc is None: return
#        reply = lirc.SendCommand(self.__lirc, remote, key).run()
#        if not reply.success:
#            self.logger.error('Unable to send command for LIRC remote "{}", key "{}": {}'.format(remote, key, reply.data[0]))
 
    # emulated version
    def keyPress(self, remote, key, downTime = None):
        if self.__lirc is None: return
        if downTime is None:
            downTime = self.keyPressDownTime
        elif downTime <= 0:
            raise DeviceException('downTime must be positive!')
            
        self.logger.debug('Send key press for LIRC remote "{}" key "{}"'.format(remote, key))
        
        reply = lirc.StartRepeatCommand(self.__lirc, remote, key).run()
        if not reply.success:
            self.logger.error('Unable to press key for LIRC remote "{}", key "{}": {}'.format(remote, key, reply.data[0]))
            
        time.sleep(downTime)
        
        reply = lirc.StopRepeatCommand(self.__lirc, remote, key).run()
        if not reply.success:
            self.logger.error('Unable to release key for LIRC remote "{}", key "{}": {}'.format(remote, key, reply.data[0]))
                
