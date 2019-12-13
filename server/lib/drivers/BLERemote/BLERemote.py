
import threading, queue, struct
import time
import bluepy.btle as bt

from hub import BaseDevice, DeviceException


serviceUUID = bt.UUID('1234')
buttonUUID = bt.UUID('0001')
ledsUUID = bt.UUID('0002')
chargingUUID = bt.UUID('0003')
resetUUID = bt.UUID('0099')
numLEDs = 5

COLORS = {
    'red': [255, 0, 0],
    'orange': [255, 128, 0],
    'yellow': [255, 255, 0],
    'lime': [128, 255, 0],
    'green': [0, 255, 0],
    'bluegreen': [0, 255, 128],
    'cyan': [0, 255, 255],
    'lightblue': [0, 128, 255],
    'blue': [0, 0, 255],
    'purple': [128, 0, 255],
    'magenta': [255, 0, 255],
    'fuschia': [255, 0, 128],
    'black': [0, 0, 0],
    'white': [255, 255, 255],
    'white50': [128, 128, 128],
}


class Device(BaseDevice):

    def configure(self, **config):
        super().configure(**config)
        self.address = config.get('address')
        if self.address is None:
            raise DeviceException('Address is required!')
        self.buttonMap = config.get('buttonMap', {})
        self.__reset()
            
    def start(self):
        if self.__run: return
        super().start()
        self.__run = True
        self.__queue = queue.Queue()
        thread = threading.Thread(target = self.__loop, name = 'BLERemote.' + self.id, daemon = True)
        thread.start()

    def stop(self):
        if not self.__run: return
        super().stop();
        self.__run = False
        # TODO: is there a way to interrupt the BLE connect process?
        #while self.__periph is not None:
        #    time.sleep(0.1)
        self.__reset()

    def __reset(self):
        self.__periph = None
        self.__buttonChar = None
        self.__ledsChar = None
        self.__chargingChar = None
        self.__resetChar = None
        self.__run = False
        self.__queue = None
        self.connected = False
        self.ledColors = [0] * (numLEDs * 3)
        self.ledColorsStack = []
        self.charging = False
    
    def __loop(self):
        self.__periph = bt.Peripheral()
        myself = self
        
        class Delegate(bt.DefaultDelegate):
            def handleNotification(self, cHandle, data):
                myself._handleNotification(cHandle, data)
        delegate = Delegate()
        self.logger.info('Started')
        
        while self.__run:
            try:
                self.logger.debug('Looking for remote...')
                self.__periph.connect(self.address, bt.ADDR_TYPE_RANDOM)
                t1 = time.time()
                self.logger.debug('state is {}'.format(self.__periph.getState()))
                service = self.__periph.getServiceByUUID(serviceUUID)
                chars = service.getCharacteristics()
        
                self.__buttonChar = next((c for c in chars if c.uuid == buttonUUID), None)
                self.__ledsChar = next((c for c in chars if c.uuid == ledsUUID), None)
                self.__chargingChar = next((c for c in chars if c.uuid == chargingUUID), None)
                self.__resetChar = next((c for c in chars if c.uuid == resetUUID), None)
        
                # set up notifications
        
                notify = struct.pack('<bb', 0x01, 0x00)
                self.__periph.writeCharacteristic(self.__buttonChar.getHandle() + 1, notify)
                self.__periph.writeCharacteristic(self.__chargingChar.getHandle() + 1, notify)

                self.__periph.withDelegate(delegate)
                t2 = time.time()
                self.logger.debug('Setup in {} seconds'.format(t2 - t1))
                self.logger.info('Connected to {}'.format(self.address))
                self.connected = True
                self.__setLEDColors(*self.ledColors)
                self.emitGenericEvent(id = 'BLERemoteConnected')

                while self.__run:
                    if not self.__queue.empty():
                        colors = self.__queue.get()
                        self.logger.debug('write LEDs: {}'.format(colors))
                        data = struct.pack('15B', *colors)
                        self.__ledsChar.write(data)
                    if self.__periph.waitForNotifications(0.1):
                        continue
            
            except bt.BTLEDisconnectError:
                self.logger.debug('Disconnected or remote not found')
                pass
            except bt.BTLEException:
                self.logger.exception('BLE exception:')
            finally:
                try:
                    self.__periph.disconnect()
                except:
                    pass
                self.connected = False
                if self.__buttonChar is not None:
                    self.logger.info('Disconnected')
                    self.emitGenericEvent(id = 'BLERemoteDisconnected')
                self.__buttonChar = None
                self.__ledsChar = None
                self.__chargingChar = None
                self.__resetChar = None
                
        self.__periph = None
        self.logger.info('Stopped')

    def _handleNotification(self, cHandle, data):
        if cHandle == self.__buttonChar.getHandle():
            self.__handleButton(data)
        elif cHandle == self.__chargingChar.getHandle():
            self.__handleCharging(data)

    def __handleButton(self, data):
        data = struct.unpack('BB', data)
        button = hex(data[1])
        state = 'down' if data[0] == 1 else 'up'
        if button in self.buttonMap:
            button = self.buttonMap[button]
        self.emitButtonEvent(button = button, state = state)
        
    def __handleCharging(self, data):
        data = struct.unpack('B', data)[0]
        self.charging = data == 1
        self.emitGenericEvent(id = 'bleRemoteBeginCharge' if data == 1 else 'bleRemoteEndCharge')
        
    def __setLEDColors(self, *colors):
        self.logger.debug('set LEDs to: {}'.format(colors))
        if not self.connected: return
        self.__queue.put(colors)

    #--------------------------------------------------------------------------
    # Public API
    #
        
    @property
    def reset(self):
        if not self.connected: return
        # TODO: what's the correct state value for this? use periph.status()?
        if self.__resetChar is not None and self.__periph.getState() == 'up':
            self.__resetChar.write(b'\x01')
    
    def pushLEDColors(self, *colors):
        self.ledColorsStack.append(self.ledColors[:])
        self.setLEDColors(*colors)
    
    def popLEDColors(self):
        if len(self.ledColorsStack) == 0: return
        self.__setLEDColors(*self.ledColorsStack.pop())
    
    def popAllLEDColors(self):
        if len(self.ledColorsStack) == 0: return
        colors = self.ledColorsStack[0]
        self.ledColorsStack = []
        self.__setLEDColors(*colors)
        
    def setLEDColors(self, *colors):
        while len(colors) < numLEDs:
            colors.append(None)
        cols = []
        for color in colors:
            if color is None:
                color = [0, 0, 0]
            elif isinstance(color, list):
                color = color[:3]
                while len(color) < 3:
                    color.append(color[-1])
            elif isinstance(color, str):
                if color not in COLORS:
                    self.logger.error('LED color "{}" is unknown'.format(color))
                    color = [0, 0, 0]
                else:
                    color = COLORS[color]
            else:
                self.logger.error('LED color "{}" is unknown'.format(color))
                color = [0, 0, 0]
            cols.extend(color)

        self.ledColors = cols
        self.__setLEDColors(*cols)
