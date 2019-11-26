
class DotDict(dict):

#    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    
   
    def __getattr__(self, k):
        if k in self:
            v = self[k]
            if isinstance(v, dict) and not instanceof(v, DotDict):
                v = DotDict(v)
                self[k] = v
            return v
        raise AttributeError("'{}' object has no attribute '{}'".format(__name__, k))
