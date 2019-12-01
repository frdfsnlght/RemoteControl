#!/usr/bin/env python3

import sys, os, struct, argparse
import bluepy
import bluepy.btle as bt

periph = bt.Peripheral()

uuids = {
    'service': bt.UUID('1234'),
    'wakeupAcceleration': bt.UUID('0005'),
    'sleepTime': bt.UUID('0007'),
    'deepSleepTime': bt.UUID('0008'),
    'saveSettings': bt.UUID('0090'),
    'reset': bt.UUID('0099')
}

characteristics = {}

def connect(address):
    try:
        periph.connect(address, bt.ADDR_TYPE_RANDOM)
        service = periph.getServiceByUUID(uuids['service'])
        chars = service.getCharacteristics()

        characteristics['wakeupAcceleration'] = next((c for c in chars if c.uuid == uuids['wakeupAcceleration']), None)
        characteristics['sleepTime'] = next((c for c in chars if c.uuid == uuids['sleepTime']), None)
        characteristics['deepSleepTime'] = next((c for c in chars if c.uuid == uuids['deepSleepTime']), None)
        characteristics['saveSettings'] = next((c for c in chars if c.uuid == uuids['saveSettings']), None)
        characteristics['reset'] = next((c for c in chars if c.uuid == uuids['reset']), None)

        print('Connected')
    except bt.BTLEDisconnectError:
        print('Unable to connect. Is the remote on the charger?')
        sys.exit(1)
            
def disconnect():
    periph.disconnect()
    characteristics.clear()
    print('Disconnected')

def writeWakeupAcceleration(value):
    data = struct.pack('f', float(value))
    characteristics['wakeupAcceleration'].write(data)
    print('Wrote wakeup acceleration {}'.format(value))
    
def readWakeupAcceleration():
    data = characteristics['wakeupAcceleration'].read()
    value = struct.unpack('f', data)
    return value[0]
    
def writeSleepTime(value):
    data = struct.pack('L', int(value))
    characteristics['sleepTime'].write(data)
    print('Wrote sleep time {}'.format(value))

def readSleepTime():
    data = characteristics['sleepTime'].read()
    value = struct.unpack('L', data)
    return value[0]
    
def writeDeepSleepTime(value):
    data = struct.pack('L', int(value))
    characteristics['deepSleepTime'].write(data)
    print('Wrote deep sleep time {}'.format(value))

def readDeepSleepTime():
    data = characteristics['deepSleepTime'].read()
    value = struct.unpack('L', data)
    return value[0]
    
def saveSettings():
    data = struct.pack('B', 1)
    characteristics['saveSettings'].write(data)
    print('Saved settings')

def reset():
    data = struct.pack('B', 1)
    characteristics['reset'].write(data)
    print('Reset')

def readValues():
    acceleration = readWakeupAcceleration()
    sleepTime = readSleepTime()
    deepSleepTime = readDeepSleepTime()
    print('Acceleration: {}Gs'.format(acceleration))
    print('Sleep time: {}ms'.format(sleepTime))
    print('Deep sleep time: {}ms'.format(deepSleepTime))

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Read/write BLERemote settings.',
            epilog = 'If no settings are specified, just displays the current values.')
    parser.add_argument('-a', '--address', type = str, required = True, help = 'the BT address of the remote')
    parser.add_argument('--acceleration', type = float, help = 'the acceleration required to wake the remote, in Gs (default 1.5)')
    parser.add_argument('--sleep', type = int, help = 'the time after which the remote goes to sleep, in milliseconds (default 10000, 0 to disable)')
    parser.add_argument('--deepsleep', type = int, help = 'the time after which the remote goes to deep sleep, in milliseconds (default 3600000)')
    parser.add_argument('--save', action = 'store_true', help = 'save settings to flash')
    parser.add_argument('--reset', action = 'store_true', help = 'reset (reboot) the remote')
    
    options = parser.parse_args(sys.argv[1:])
    connect(options.address)
    if options.acceleration:
        writeWakeupAcceleration(options.acceleration)
    if options.sleep:
        writeSleepTime(options.sleep)
    if options.deepsleep:
        writeDeepSleepTime(options.deepsleep)
        
    readValues()
    
    if options.save:
        saveSettings()
    if options.reset:
        reset()

    disconnect()
    
        