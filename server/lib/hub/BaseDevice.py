
import logging
from event_bus import EventBus

import hub


class DeviceException(Exception):
    pass
    
    
class BaseDevice():

    def __init__(self, id):
        self.id = id
        self.logger = logging.getLogger('Device.' + id)
        self.eventBus = EventBus()
        self.state = hub.DotDict()
        
    def configure(self, **config):
        self.state.update(config.get('state', {}))

    def start(self):
        self.logger.info('Starting...')
        
    def stop(self):
        self.logger.info('Stopping...')
        
    def emitGenericEvent(self, id, **args):
        self.eventBus.emit('generic', id = id, device = self, **args)
        
    def emitButtonEvent(self, button, state):
        self.eventBus.emit('button', button = button, state = state, device = self)
        