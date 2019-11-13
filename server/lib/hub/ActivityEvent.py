
import hub


class ActivityEvent():

    def __init__(self, id, activity):
        self.id = id
        self.activity = activity
        self.state = hub.DotDict()
        
    def configure(self, **config):
        source = 'Activity "{}", Event "{}"'.format(self.activity.id, self.id)
        self.code = config.get('code')
        if self.code is not None:
            self.code = compile(str(self.code), source, 'exec')

