
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
        self.state.update(config.get('state', {}))
        self.basedOn = config.get('basedOn', [])
        self.buttons = config.get('buttons', {})
        self.events = config.get('events', {})
        self.ignoreButtons = config.get('ignoreButtons', [])
        self.ignoreEvents = config.get('ignoreEvents', [])
        
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

        self.__inheritButtons()
        self.__inheritEvents()
        
#    def __inheritProperty(self, prop):
#        if getattr(self, prop) is None:
#            for act in self.basedOn:
#                val = getattr(act, prop)
#                if val is not None:
#                    setattr(self, prop, val)
#                    break
    
    def __inheritButtons(self):
        if self.ignoreButtons == 'all': return
        ignore = set(self.ignoreButtons)
        for act in self.basedOn:
            for (k, v) in act.buttons.items():
                if k in ignore: continue
                if k in self.buttons: continue
                self.buttons[k] = v
                
    def __inheritEvents(self):
        if self.ignoreEvents == 'all': return
        ignore = set(self.ignoreEvents)
        for act in self.basedOn:
            for (k, v) in act.events.items():
                if k in ignore: continue
                if k in self.events: continue
                if k + '+' in self.events:
                    myV = self.events[k + '+']
                    del(self.events[k + '+'])
                    self.events[k] = []
                    if isinstance(v, list):
                        self.events[k].extend(v)
                    else:
                        self.events[k].append(v)
                    self.events[k].append(myV)
                elif '+' + k in self.events:
                    myV = self.events['+' + k]
                    del(self.events['+' + k])
                    self.events[k] = [myV]
                    if isinstance(v, list):
                        self.events[k].extend(v)
                    else:
                        self.events[k].append(v)
                else:
                    self.events[k] = v
                    
        # cleanup
        for (k, v) in {**self.events}.items():
            if k[:1] == '+':
                self.events[k[1:]] = self.events[k]
                del(self.events[k])
            elif k[-1:] == '+':
                self.events[k[:-1]] = self.events[k]
                del(self.events[k])
                