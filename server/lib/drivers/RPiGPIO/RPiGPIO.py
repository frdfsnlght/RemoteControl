
# See http://abyz.me.uk/rpi/pigpio/python.html

import pigpio

from hub import BaseDevice, DeviceException, Timer


class Pin():

    def __init__(self, pin, device):
        self.pin = pin
        self.device = device

    def configure(self, **config):
        self.name = config.get('name', self.pin)
        self.mode = str(config.get('mode', 'input')).lower()
        if self.mode == 'input' or self.mode == 'in':
            self.mode == 'input'
            
            self.pullUpDown = str(config.get('pullUpDown')).lower()
            if self.pullUpDown == 'none':
                self.pullUpDown = None
            elif self.pullUpDown not in ['up', 'down']:
                raise DeviceException('Pin {} pullUpDown is invalid!'.format(self.pin))
                
            self.edge = str(config.get('edge')).lower()
            if self.edge == 'none':
                self.edge = None
            elif self.edge not in ['rising', 'falling', 'both']:
                raise DeviceException('Pin {} edge is invalid!'.format(self.pin))
                
            self.debounceTime = config.get('debounceTime')
            if self.debounceTime is not None and self.debounceTime > 0.3:
                raise DeviceException('Pin {} debounceTime is greater than 0.3 seconds!'.format(self.pin))
                
            if self.edge is not None:
                self.eventType = str(config.get('eventType', 'generic')).lower()
                if self.eventType not in ['generic', 'button']:
                    raise DeviceException('Pin {} eventType is invalid!'.format(self.pin))
                if self.eventType == 'generic':
                    self.fallingEventId = config.get('fallingEventId')
                    self.risingEventId = config.get('risingEventId')
                elif self.eventType == 'button':
                    self.button = config.get('button')
                    if self.button is None:
                        raise DeviceException('Pin {} missing button!'.format(self.pin))
                    self.buttonDown = str(config.get('buttonDown', 'falling')).lower()
                    if self.buttonDown not in ['falling', 'rising']:
                        raise DeviceException('Pin {} buttonDown is invalid!'.format(self.pin))
                
        elif self.mode == 'output' or self.mode == 'out':
            self.mode == 'output'
            self.level = self.resolveLevel(config.get('level'))
        
        elif self.mode == 'hardpwm':
            self.mode = 'hardPWM'
            self.frequency = config.get('frequency', 0)
            self.dutyCycle = config.get('dutyCycle', 0)
        
        elif self.mode == 'softpwm':
            self.mode = 'softPWM'
            self.frequency = config.get('frequency', 0)
            self.dutyCycle = config.get('dutyCycle', 0)
            self.pwmTimer = None
        
        else:
            raise DeviceException('Pin {} mode is invalid!'.format(self.pin))

    def start(self):
        pi = self.device.pi
        
        if self.mode == 'input':
            pud = pigpio.PUD_NONE if self.pullUpDown is None else pigpio.PUD_UP if self.pullUpDown == 'up' else pigpio.PUD_DOWN
            pi.set_mode(self.pin, pigpio.INPUT)
            pi.set_pull_up_down(self.pin, pud)
            if self.debounceTime is not None and self.debounceTime > 0:
                pi.set_glitch_filter(self.pin, int(self.debounceTime * 1000000))

            if self.edge is not None:
                edge = {'rising': pigpio.RISING_EDGE, 'falling': pigpio.FALLING_EDGE, 'both': pigpio.EITHER_EDGE}[self.edge]
                self.callback = pi.callback(self.pin, edge, self.inputCallback)
                
        elif self.mode == 'output':
            pi.set_mode(self.pin, pigpio.OUTPUT)
            self.setOutput(self.output)
        elif self.mode == 'hardPWM':
            self.setPWM(self, self.frequency, self.dutyCycle)
        elif self.mode == 'softPWM':
            pi.set_mode(self.pin, pigpio.OUTPUT)
            self.setupSoftwarePWM()

    def stop(self):
        if self.mode == 'input':
            if self.edge is not None and self.callback is not None:
                self.callback.cancel()
                self.callback = None
                
        elif self.mode == 'hardPWM':
            self.setPWM(0, 0)
        elif self.mode == 'softPWM':
            self.setPWM(0, 0)
            

    def inputCallback(self, pin, level, tick):
        if level == 2: return
        level = level == 1
        print('pin {} is {}'.format(self.pin, level))
        if self.eventType == 'generic':
            id = self.risingEventId if level else self.fallingEventId
            if id is not None:
                self.device.emitGenericEvent(id = id, payload = {'pin': self.pin, 'name': self.name, 'level': level})
        elif self.eventType == 'button':
            state = 'down' if ((not level and self.buttonDown == 'falling') or (level and self.buttonDown == 'rising')) else 'up'
            self.device.emitButtonEvent(button = self.button, state = state)
        
    def getInput(self):
        if self.mode != 'input':
            raise DeviceException('Pin "{}" ({}) is not an input!'.format(self.name, self.pin))
        return self.device.pi.read(self.pin) == 1
        
    def setOutput(self, level):
        if self.mode != 'output':
            raise DeviceException('Pin "{}" ({}) is not an output!'.format(self.name, self.pin))
        level = self.resolveLevel(level)
        self.device.pi.write(self.pin, 1 if level else 0)

    def setPWM(self, frequency, dutyCycle):
        if self.mode == 'hardPWM':
            self.setPWMFrequency(frequency)
            self.setPWMDutyCycle(dutyCycle)
        elif self.mode == 'softPWM':
            self.frequency = frequency
            self.dutyCycle = dutyCycle
            self.setupSoftwarePWM()
        else:
            raise DeviceException('Pin "{}" ({}) is not PWM!'.format(self.name, self.pin))
        
    def setPWMFrequency(self, frequency):
        self.frequency = frequency
        if self.mode == 'hardPWM':
            self.device.pi.set_PWM_frequency(frequency)
        elif self.mode == 'softPWM':
            self.setupSoftwarePWM()
        else:
            raise DeviceException('Pin "{}" ({}) is not PWM!'.format(self.name, self.pin))
        
    def setPWMDutyCycle(self, dutyCycle):
        self.dutyCycle = dutyCycle
        if self.mode == 'hardPWM':
            self.device.pi.set_PWM_dutycycle(int(dutyCycle * 255))
        elif self.mode == 'softPWM':
            self.setupSoftwarePWM()
        else:
            raise DeviceException('Pin "{}" ({}) is not PWM!'.format(self.name, self.pin))

    def setupSoftwarePWM(self):
        if self.frequency == 0 or self.dutyCycle == 0:
            self.device.pi.write(self.pin, 0)
            if self.pwmTimer is not None:
                self.pwmTimer.cancel()
                self.pwmTimer = None
        elif self.dutyCycle == 1:
            self.device.pi.write(self.pin, 1)
            if self.pwmTimer is not None:
                self.pwmTimer.cancel()
                self.pwmTimer = None
        else:
            self.device.pi.write(self.pin, 1)
            if self.pwmTimer is None:
                self.pwmTimer = Timer(self.dutyCycle / self.frequency, self.pwmTimerLow, repeat = True)
                self.pwmTimer.start()
            else:
                self.pwmTimer.reset(self.dutyCycle / self.frequency, self.pwmTimerLow)
                
    def pwmTimerLow(self):
        self.device.pi.write(self.pin, 0)
        self.pwmTimer.reset((1 - self.dutyCycle) / self.frequency, self.pwmTimerHigh)
        
    def pwmTimerHigh(self):
        self.device.pi.write(self.pin, 1)
        self.pwmTimer.reset(self.dutyCycle / self.frequency, self.pwmTimerLow)
    
    def resolveLevel(self, level = None):
        return level in [1, True, 'true', 'high']
   
        
class Device(BaseDevice):

    def configure(self, **config):
        super().configure(**config)
        self.address = config.get('address', '127.0.0.1')
        self.port = config.get('port', 8888)
        pins = config.get('pins')
        if not isinstance(pins, dict):
            raise DeviceException('Pins are not defined!')
            
        self.__reset()
        self.pinsByPin = {}
        self.pinsByName = {}
        
        for (pinId, pinConf) in pins.items():
            pin = Pin(pinId, self)
            pin.configure(**pinConf)
            self.pinsByPin[pin.pin] = pin
            self.pinsByName[pin.name] = pin
            
    def start(self):
        if self.pi and self.pi.connected: return
        super().start()

        self.pi = pigpio.pi(self.address, self.port)
        if not self.pi.connected:
            self.logger.error('Unable to connect Pi at {}:{}!'.format(self.address, self.port))
            self.pi = None
            return
            
        for pin in self.pinsByPin.values():
            pin.start()
            
        self.logger.info('Connected to Pi at {}:{}'.format(self.address, self.port))
       
    def stop(self):
        if self.pi is None or not self.pi.connected: return
        super().stop()

        for pin in self.pinsByPin.values():
            pin.stop()
        self.pi.stop()
        self.logger.info('Disconnected from Pi at {}:{}'.format(self.address, self.port))
        
        self.__reset()

    def __reset(self):
        self.pi = None
        self.pinsByPin = None
        self.pinsByName = None

    def __findPin(self, pinOrName):
        pin = self.pinsByPin.get(pinOrName)
        if pin is None: pin = self.pinsByName.get(pinOrName)
        if pin is None:
            raise DeviceException('Pin "{}" is unknown!', pinOrName)
        return pin
            
    def __getattr__(self, attr):
        return self.__findPin(attr)
        
    #--------------------------------------------------------------------------
    # Public API
    #

    def getInput(self, pinOrName):
        if self.pi is None or not self.pi.connected: return None
        pin = self.__findPin(pinOrName)
        return pin.getInput()
            
    def setOuput(self, pinOrName, level):
        if self.pi is None or not self.pi.connected: return None
        pin = self.__findPin(pinOrName)
        pin.setOutput(level)
    
    def setPWM(self, pinOrName, frequency, dutyCycle):
        if self.pi is None or not self.pi.connected: return None
        pin = self.__findPin(pinOrName)
        pin.setPWM(frequency, dutyCycle)
    
    def setPWMFrequency(self, pinOrName, frequency):
        if self.pi is None or not self.pi.connected: return None
        pin = self.__findPin(pinOrName)
        pin.setPWMFrequency(frequency)
    
    def setPWMDutyCycle(self, pinOrName, dutyCycle):
        if self.pi is None or not self.pi.connected: return None
        pin = self.__findPin(pinOrName)
        pin.setPWMDuty(dutyCycle)
    
