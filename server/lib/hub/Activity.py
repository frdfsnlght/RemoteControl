
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
        buttons = config.get('buttons', {})
        events = config.get('events', {})
        self.ignoreButtons = config.get('ignoreButtons', [])
        self.ignoreEvents = config.get('ignoreEvents', [])
        
        self.buttons = {}
        for (btnId, btnConf) in buttons.items():
            button = ActivityButton(btnId, self)
            if isinstance(btnConf, str):
                button.configure(onDown = btnConf)
            else:
                button.configure(**btnConf)
            self.buttons[button.id] = button
            
        self.events = {}
        self.prefixEvents = {}
        self.postfixEvents = {}
        for (evtId, evtCode) in events.items():
            event = ActivityEvent(evtId, self)
            event.configure(code = evtCode)
            if event.override == 'prefix':
                self.prefixEvents[event.id] = event
            elif event.override == 'postfix':
                self.postfixEvents[event.id] = event
            else:
                self.events[event.id] = event

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
        self.basedOn = basedOn

        if isinstance(self.ignoreButtons, list):
            for act in self.basedOn:
                for (id, actButton) in act.buttons.items():
                    if id in self.ignoreButtons: continue
                    if id in self.buttons: continue
                    self.buttons[id] = actButton
        
        if isinstance(self.ignoreEvents, list):
            for act in self.basedOn:
                for (id, actEvent) in act.events.items():
                    if id in self.ignoreEvents: continue
                    
                    if id not in self.events:
                        if isinstance(actEvent, list):
                            self.events[id] = [*actEvent]
                        else:
                            self.events[id] = actEvent
                        
                    if id in self.prefixEvents:
                        myEvent = self.prefixEvents[id]
                        if isinstance(self.events[id], list):
                            self.events[id].insert(0, myEvent)
                        else:
                            self.events[id] = [myEvent, self.events[id]]
                            
                    if id in self.postfixEvents:
                        myEvent = self.postfixEvents[id]
                        if isinstance(self.events[id], list):
                            self.events[id].append(myEvent)
                        else:
                            self.events[id] = [self.events[id], myEvent]
                    
        del(self.prefixEvents)
        del(self.postfixEvents)
        
                    
    def __str__(self):
        return 'Activity({}, buttons={}, events={})'.format(
            self.id,
            ', '.join([str(x) for x in self.buttons.values()]),
            ', '.join([str(x) for x in self.events.values()])
        )
        
    __repr__ = __str__
