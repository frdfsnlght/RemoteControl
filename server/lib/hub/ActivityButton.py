
import re

import hub


class ActivityButton():

    def __init__(self, id, activity):
        self.id = id
        self.activity = activity
        self.state = hub.DotDict()
        
    def configure(self, **config):
        repeat = config.get('repeat')
        if repeat is not None:
            (interval, delay) = (re.split(r'\s*,?\s+', str(repeat)) + [None, None])[:2]
            if interval is not None:
                interval = float(interval)
                if interval <= 0: interval = None
            self.repeatInterval = interval
            if delay is not None:
                delay = float(delay)
                if delay <= 0: delay = None
            self.repeatDelay = delay
        else:
            self.repeatDelay = config.get('repeatDelay')
            self.repeatInterval = config.get('repeatInterval')
            
        hold = config.get('hold')
        if hold is not None:
            hold = float(hold)
            if hold <= 0: hold = None
        self.hold = hold
        
        source = 'Activity "{}", Button "{}"'.format(self.activity.id, self.id)
        
        self.__compileCode(config, 'onDown', source)
        self.__compileCode(config, 'onUp', source)
        self.__compileCode(config, 'onHold', source)
        
    def __compileCode(self, config, key, source):
        code = config.get(key)
        if code is not None:
            code = compile(str(code), source + ', ' + key, 'exec')
        setattr(self, key, code)

        
            