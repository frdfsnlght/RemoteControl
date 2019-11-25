
import threading, struct
import time
import bluepy.btle as bt

from hub import BaseDevice, DeviceException


serviceUUID = bt.UUID('1234')
buttonUUID = bt.UUID('0001')
ledsUUID = bt.UUID('0002')
chargingUUID = bt.UUID('0003')
batteryLevelUUID = bt.UUID('0004')
resetUUID = bt.UUID('0099')
numLEDs = 5


class Device(BaseDevice):

    def configure(self, **config):
        self.address = config.get('address')
        if self.address is None:
            raise DeviceException('Address is required!')
        self.buttonMap = config.get('buttonMap', {})

        self.__periph = None
        self.__buttonChar = None
        self.__ledsChar = None
        self.__chargingChar = None
        self.__batteryLevelChar = None
        self.__resetChar = None
        self.__run = False
        self.connected = False
        self.ledColors = [0] * (numLEDs * 3)
        self.charging = False
        self.batteryLevel = 0
            
    def start(self):
        if self.__run: return
        super().start()
        self.__run = True
        thread = threading.Thread(target = self.__loop, name = 'BLERemote.' + self.id, daemon = True)
        thread.start()

    def stop(self):
        if not self.__run: return
        super().stop();
        self.__run = False
        # TODO: is there a way to interrupt the BLE connect process?
        #while self.__periph is not None:
        #    time.sleep(0.1)
        
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
                self.__batteryLevelChar = next((c for c in chars if c.uuid == batteryLevelUUID), None)
                self.__resetChar = next((c for c in chars if c.uuid == resetUUID), None)
        
                # set up notifications
        
                notify = struct.pack('<bb', 0x01, 0x00)
                self.__periph.writeCharacteristic(self.__buttonChar.getHandle() + 1, notify)
                self.__periph.writeCharacteristic(self.__chargingChar.getHandle() + 1, notify)
                self.__periph.writeCharacteristic(self.__batteryLevelChar.getHandle() + 1, notify)

                self.__periph.withDelegate(delegate)
                t2 = time.time()
                self.logger.debug('Setup in {} seconds'.format(t2 - t1))
                self.logger.info('Connected to {}'.format(self.address))
                self.connected = True
                self.__setLEDColors(*self.ledColors)
                self.emitGenericEvent(id = 'BLERemoteConnected')

                while self.__run:
                    if remote.waitForNotifications(0.5):
                        continue
            
            except bt.BTLEDisconnectError:
                self.logger.debug('Disconnected or remote not found')
                pass
            except bt.BTLEException:
                self.logger.exception('BLE exception:')
            finally:
                self.__periph.disconnect()
                self.connected = False
                if self.__buttonChar is not None:
                    self.logger.info('Disconnected')
                    self.emitGenericEvent(id = 'BLERemoteDisconnected')
                self.__buttonChar = None
                self.__ledsChar = None
                self.__chargingChar = None
                self.__batteryLevelChar = None
                self.__resetChar = None
                
        self.__periph = None
        self.logger.info('Stopped')

    def _handleNotification(self, cHandle, data):
        if cHandle == self.__buttonChar.getHandle():
            self.__handleButton(data)
        elif cHandle == self.__chargingChar.getHandle():
            self.__handleCharging(data)
        elif cHandle == self.__batteryLevelChar.getHandle():
            self.__handleBatteryLevel(data)

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
        
    def __handleBatteryLevel(self, data):
        data = struct.unpack('f', data)[0]
        self.batteryLevel = data
        self.emitGenericEvent(id = 'bleRemoteBatteryLevelChanged')

    def __setLEDColors(self, *colors):
        if not self.connected: return
        data = struct.pack('15B', *colors)
        self.ledsChar.write(data)

    #--------------------------------------------------------------------------
    # Public API
    #
        
    @property
    def reset(self):
        if not self.connected: return
        # TODO: what's the correct state value for this? use periph.status()?
        if self.__resetChar is not None and self.__periph.getState() == 'up':
            self.__resetChar.write(b'\x01')

    def setLEDColors(self, *colors):
        cols = []
        if any(isinstance(item, list) for item in colors):
            # provided a list of lists
            for color in colors[:numLEDs]:
                if not isinstance(color, list):
                    color = [0, 0, 0]
                else:
                    color = color[:3]
                    while len(color) < 3:
                        color.append(color[-1])
                cols.extend(color)
        else:
            cols = colors[:numLEDs * 3]
            while len(cols) < numLEDs * 3:
                cols.append(0)

        self.ledColors = cols
        self.__setLEDColors(*cols)
