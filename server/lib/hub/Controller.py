
import logging, threading, queue, time

import hub


class ControllerException(Exception):
    pass
    
class Exit(Exception):
    pass
    
class ExitLocal(Exception):
    pass
    
class ControllerEvent():

    def __init__(self, type, device = None):
        self.type = type
        self.device = device

class GenericControllerEvent(ControllerEvent):

    def __init__(self, id, device = None, **args):
        super().__init__('generic', device)
        self.id = id
        self.args = args
        
    def __str__(self):
        return '{{type: {}, device: {}, id: {}, args: {}}}'.format(
                self.type, self.device.id if self.device else 'None', self.id, self.args)
            
class ButtonControllerEvent(ControllerEvent):

    def __init__(self, button, state, device = None):
        super().__init__('button', device)
        self.button = button
        self.state = state
        self.cancelled = False

    @property
    def cancel(self):
        self.cancelled = True
        
    def __str__(self):
        return '{{type: {}, device: {}, button: {}, state: {}}}'.format(
                self.type, self.device.id if self.device else 'None', self.button, self.state)
        
class DownButton():

    def __init__(self, controller, button):
        self.controller = controller
        self.button = button
        self.event = None
        self.hold = False
        self.repeatTimer = None
        self.holdTimer = None
        
    def down(self, event):
        self.event = event
        
        if self.button.onDown is not None:
            self.controller._execCode(self.button.onDown, locals = self.button.state, event = event, button = self.button)
            interval = self.button.repeatInterval
            delay = self.button.repeatDelay
            if interval is not None:
                if delay is not None:
                    self.repeatTimer = threading.Timer(delay, self.__afterRepeatDelay)
                    self.repeatTimer.start()
                else:
                    self.__afterRepeatDelay()
                    
        if self.button.hold is not None and self.button.onHold is not None:
            self.holdTimer = threading.Timer(self.button.hold, self.__afterHold)
            self.holdTimer.start()
        
        
    def up(self, event):
        self.event = event
        if self.repeatTimer is not None: self.repeatTimer.cancel()
        if self.holdTimer is not None: self.holdTimer.cancel()
        if self.button.onUp is not None:
            self.controller._execCode(self.button.onUp, locals = self.button.state, event = event, button = self.button)
        
    def __afterRepeatDelay(self):
        interval = self.button.repeatInterval
        if interval is not None:
            self.repeatTimer = threading.Timer(interval, self.__repeatDown)
            self.repeatTimer.start()
            
    def __repeatDown(self):
        self.controller._execCode(self.button.onDown, locals = self.button.state, event = self.event, button = self.button)
        self.repeatTimer = threading.Timer(self.repeatTimer.interval, self.__repeatDown)
        self.repeatTimer.start()
        
    def __afterHold(self):
        if self.repeatTimer is not None: self.repeatTimer.cancel()
        self.controller._execCode(self.button.onHold, locals = self.button.state, event = self.event, button = self.button)
        interval = self.button.repeatInterval
        if interval is not None:
            self.repeatTimer = threading.Timer(interval, self.__repeatHold)
            self.repeatTimer.start()
        
    def __repeatHold(self):
        self.controller._execCode(self.button.onHold, locals = self.button.state, event = self.event, button = self.button)
        self.repeatTimer = threading.Timer(self.repeatTimer.interval, self.__repeatHold)
        self.repeatTimer.start()
    
    
    
class Controller():

    def __init__(self, id):
        self.id = id
        self.logger = logging.getLogger('Controller.' + id)
        self.run = False
        self.thread = None
        self.eventQueue = queue.Queue()
        self.currentActivity = None
        self.downButtons = {}
        self.state = hub.DotDict()
        self.execGlobals = {
            'hub': hub,
            'devices': hub.devices,
            'activities': hub.activities,
            'controllers': hub.controllers,
            'controller': self,
            'gState': hub.state,
            'cState': self.state,
            'activity': None,
            'aState': None,
            'logger': None,
            
            'switchToActivity': self.switchToActivity,
            'pushActivity': self.pushActivity,
            'popActivity': self.popActivity,
            'popAllActivities': self.popAllActivities,
            'triggerGenericEvent': self.triggerGenericEvent,
            
            'Exit': Exit,
            'ExitLocal': ExitLocal,
            
            'sleep': time.sleep, # TODO: move this to the Imports based device
            'time': time.time # TODO: move this to the Imports based device
        }
        
    def configure(self, **config):
        self.state.update(config.get('state', {}))
        actId = config.get('startActivity')
        if actId is None:
            raise ControllerException('No start activity defined!')
        if actId not in hub.activities:
            raise ControllerException('Unknown start activity: {}'.format(actId))
        self.startActivity = hub.activities[actId]
        
        deviceIds = config.get('eventDevices', [])
        if len(deviceIds) == 0:
            raise ControllerException('No event devices defined!')
        self.eventDevices = []
        for deviceId in deviceIds:
            if deviceId not in hub.devices:
                raise ControllerException('Unknown event device: {}'.format(deviceId))
            device = hub.devices[deviceId]
            if device not in self.eventDevices:
                device.eventBus.add_event(self.submitGenericEvent, 'generic')
                device.eventBus.add_event(self.submitButtonEvent, 'button')
                self.eventDevices.append(device)
        self.logger.info('{} event devices registered'.format(len(self.eventDevices)))
            
        
    def start(self):
        if self.run: return
        self.logger.info('Starting...')
        self.run = True
        self.thread = threading.Thread(target = self.__eventLoop, name = 'Controller.' + self.id, daemon = True)
        self.switchToActivity(self.startActivity)
        self.thread.start()
    
    def stop(self):
        if not self.run: return
        self.logger.info('Stopping...')
        self.run = False
        while self.thread is not None:
            time.sleep(0.1)
        self.currentActivity = None
        
    def submitGenericEvent(self, id, device = None, **args):
        self.eventQueue.put(GenericControllerEvent(id, device, **args))
        
    def submitButtonEvent(self, button, state, device = None):
        self.eventQueue.put(ButtonControllerEvent(button, state, device))
    
    def switchToActivity(self, activity):
        if activity is None:
            self.logger.error('Unable to switch to None activity!')
            return
        if not isinstance(activity, hub.Activity):
            act = hub.activities.get(str(activity))
            if act is None:
                self.logger.error('Unable to switch to unknown activity {}!'.format(str(activity)))
                return
            activity = act

        if self.currentActivity == activity: return
        self.__switchToActivity(activity)
        
    def pushActivity(self, activity):
        if activity is None:
            self.logger.error('Unable to push None activity!')
            return
        if not isinstance(activity, hub.Activity):
            act = hub.activities.get(str(activity))
            if act is None:
                self.logger.error('Unable to push unknown activity {}!'.format(str(activity)))
                return
            activity = act

        self.activityStack.append(self.currentActivity)
        self.__switchToActivity(activity)
        
    def popActivity(self):
        if len(self.activityStack) == 0: return
        activity = self.activityStack.pop()
        self.__switchToActivity(activity)

    def popAllActivities(self):
        if len(self.activityStack) == 0: return
        activity = self.activityStack[0]
        self.activityStack = []
        self.__switchToActivity(activity)

    def __switchToActivity(self, activity):
        if self.currentActivity is not None:
            self.execGlobals['nextActivity'] = activity
            self.execGlobals['previousActivity'] = None
            self.triggerGenericEvent('onActivityEnd')
            
        self.execGlobals['previousActivity'] = self.currentActivity
        self.execGlobals['nextActivity'] = None
        self.currentActivity = activity
        self.execGlobals['activity'] = activity
        self.execGlobals['aState'] = activity.state
        self.execGlobals['logger'] = activity.logger
        
        self.logger.info('Switched to activity "{}"'.format(self.currentActivity.id))
        self.triggerGenericEvent('onActivityBegin')
    
    def triggerGenericEvent(self, idOrEvent, **args):
        event = None
        if isinstance(idOrEvent, str):
            event = self.currentActivity.events.get(idOrEvent)
        else:
            event = idOrEvent
        if event is None:
            if idOrEvent is not None:
                self.logger.debug('Unhandled event: {}'.format(idOrEvent))
            return
        self.__triggerGenericEvent(event, device = None, **args)
        
    def __eventLoop(self):
        self.logger.info('Event loop started')
        while self.run:
            try:
                event = self.eventQueue.get(timeout = 0.5)
                self.logger.debug('dispatch {}'.format(event))
                if event.type == 'button':
                    self.__dispatchButtonEvent(event)
                elif event.type == 'generic':
                    self.__dispatchGenericEvent(event)
            except queue.Empty:
                pass
        self.logger.info('Event loop stopped')
        self.thread = None

    def __dispatchButtonEvent(self, event):
        e = self.currentActivity.events.get('onBeforeButton')
        if e is not None:
            self._execCode(e.code, locals = e.state, event = event)
            if event.cancelled:
                self.logger.debug('Button event cancelled: {}'.format(event))
                return

        if event.state == 'down':
            self.__handleButtonDown(event)
        elif event.state == 'up':
            self.__handleButtonUp(event)
        else:
            self.logger.error('Invalid button event state: {}'.format(event))

    def __handleButtonDown(self, event):
        db = self.downButtons.get(event.button)
        if db is not None:
            return
        button = self.currentActivity.buttons.get(event.button)
        if button is None:
            return
        db = DownButton(self, button)
        self.downButtons[button.id] = db
        db.down(event)
        
    def __handleButtonUp(self, event):
        db = self.downButtons.get(event.button)
        if db is None:
            return
        button = db.button
        del(self.downButtons[button.id])
        db.up(event)

    def __dispatchGenericEvent(self, event):
        id = event.id
        actEvent = self.currentActivity.events.get(id)
        if actEvent is None:
            self.logger.debug('Unhandled event: {}'.format(event))
            return
        self.__triggerGenericEvent(actEvent, device = event.device, **event.args)
        
    def __triggerGenericEvent(self, actEvent, device = None, **args):
        if isinstance(actEvent, list):
            for e in actEvent:
                if not self._execCode(e.code, event = e, locals = e.state, args = args):
                    return
        else:
            self._execCode(actEvent.code, event = actEvent, locals = actEvent.state, args = args)
    
    def _execCode(self, code, locals = {}, event = None, button = None, args = {}):
        self.execGlobals['event'] = event
        self.execGlobals['button'] = button
        self.execGlobals['args'] = args
        try:
            exec(code, self.execGlobals, locals)
            return True
        except Exit:
            self.logger.debug('Exiting global scope')
            return False
        except ExitLocal:
            self.logger.debug('Exiting local scope')
            return True
        except:
            self.logger.exception('Exception raised during code execution:')
            return False
