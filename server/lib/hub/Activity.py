
import logging

import hub
from .ActivityButton import ActivityButton
from .ActivityEvent import ActivityEvent


class ActivityException(Exception):
    pass
    
    
class Activity():

    def __init__(self, id):
        self.id = id
        self.logger = logging.getLogger('Activity.' + id)
        self.buttons = {}
        self.events = {}
        self.initialized = False
        self.state = hub.DotDict()
        
    def configure(self, **config):
        self.basedOn = config.get('basedOn', [])
        self.buttons = config.get('buttons', {})
        self.events = config.get('events', {})
        self.buttonsIgnore = config.get('buttonsIgnore', [])
        self.eventsIgnore = config.get('eventsIgnore', [])
        
        for (btnId, btnConf) in self.buttons.items():
            button = ActivityButton(btnId, self)
            if isinstance(btnConf, str):
                button.configure(onDown = btnConf)
            else:
                button.configure(**btnConf)
            self.buttons[btnId] = button
            
        for (evtId, evtCode) in self.events.items():
            event = ActivityEvent(evtId, self)
            event.configure(code = evtCode)
            self.events[evtId] = event
            

    def initialize(self):
        if self.initialized: return
        self.logger.info('Initializing...')
        self.initialized = True
        
        basedOn = self.basedOn
        if isinstance(basedOn, str):
            basedOn = [basedOn]
        elif not isinstance(basedOn, list):
            basedOn = []
        for i in range(len(basedOn)):
            id = basedOn[i]
            if id not in hub.activities:
                raise ActivityException('Activity "{}" does not exist!'.format(id))
            basedOn[i] = hub.activities[id]
            basedOn[i].initialize()
        basedOn.reverse()
        self.basedOn = basedOn

        self.__inheritDictionary('buttons')
        self.__inheritDictionary('events')

        
    def __inheritProperty(self, prop):
        if getattr(self, prop) is None:
            for act in self.basedOn:
                val = getattr(act, prop)
                if val is not None:
                    setattr(self, prop, val)
                    break
    
    def __inheritDictionary(self, attr):
        myDict = getattr(self, attr)
        myIgnore = set(getattr(self, attr + 'Ignore'))
        if myIgnore is not None and myIgnore == 'all':
            return
        for act in self.basedOn:
            actDict = getattr(act, attr)
            actIgnore = set(getattr(act, attr + 'Ignore'))
            myIgnore = myIgnore | actIgnore
            for (k, v) in actDict.items():
                if k not in myIgnore and k not in myDict:
                    myDict[k] = v
        
        