
import hub


class ActivityEvent():

    def __init__(self, id, activity):
        if id[:1] == '+':
            self.id = id[1:]
            self.override = 'prefix'
        elif id[-1:] == '+':
            self.id = id[:-1]
            self.override = 'postfix'
        else:
            self.id = id
            self.override = 'replace'
        self.activity = activity
        self.state = hub.DotDict()
        
    def configure(self, **config):
        source = 'Activity "{}", Event "{}"'.format(self.activity.id, self.id)
        self.code = config.get('code')
        if self.code is not None:
            self.code = compile(str(self.code), source, 'exec')

    def __str__(self):
        return 'Event({}.{})'.format(self.activity.id, self.id)

    __repr__ = __str__
        