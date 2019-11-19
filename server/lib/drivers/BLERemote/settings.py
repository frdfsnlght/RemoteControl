#!/usr/bin/env python3

import sys, os, struct, argparse
import bluepy
import bluepy.btle as bt


serviceUUID = bt.UUID('1234')
wakeupAccelerationUUID = bt.UUID('0005');
lowBatterLevelUUID = bt.UUID('0006');
sleepTimeUUID = bt.UUID('0007');
resetUUID = bt.UUID('0099');

periph = None
wakeupAccelerationChar = None
lowBatterLevelChar = None
sleepTimeChar = None
resetChar = None

def connect(address):
    global periph, wakeupAccelerationChar, lowBatterLevelChar, sleepTimeChar, resetChar
    periph = bt.Peripheral()
    try:
        periph.connect(address, bt.ADDR_TYPE_RANDOM)
        service = periph.getServiceByUUID(serviceUUID)
        chars = service.getCharacteristics()

        wakeupAccelerationChar = next((c for c in chars if c.uuid == wakeupAccelerationUUID), None)
        lowBatterLevelChar = next((c for c in chars if c.uuid == lowBatterLevelUUID), None)
        sleepTimeChar = next((c for c in chars if c.uuid == sleepTimeUUID), None)
        resetChar = next((c for c in chars if c.uuid == resetUUID), None)

        print('Connected')
    except bt.BTLEDisconnectError:
        print('Unable to connect. Is the remote on the charger?')
        sys.exit(1)
            
def disconnect():
    global periph, wakeupAccelerationChar, lowBatterLevelChar, sleepTimeChar, resetChar
    periph.disconnect()
    periph = None
    wakeupAccelerationChar = None
    lowBatterLevelChar = None
    sleepTimeChar = None
    resetChar = None
    print('Disconnected')

def writeWakeupAcceleration(value):
    data = struct.pack('f', float(value))
    wakeupAccelerationChar.write(data)
    print('Wrote wakeup acceleration')
    
def readWakeupAcceleration():
    data = wakeupAccelerationChar.read()
    value = struct.unpack('f', data)
    return value
    
def writeLowBatteryLevel(value):
    data = struct.pack('B', int(value))
    lowBatterLevelChar.write(data)
    print('Wrote low battery level')

def readLowBatteryLevel():
    data = lowBatteryLevelChar.read()
    value = struct.unpack('B', data)
    return value
    
def writeSleepTime(value):
    data = struct.pack('L', int(value))
    sleepTimeChar.write(data)
    print('Wrote sleep time')

def readSleepTime():
    data = sleepTimeChar.read()
    value = struct.unpack('L', data)
    return value
    
def reset():
    data = struct.pack('B', 1)
    resetChar.write(data)
    print('Wrote reset')

def readValues():
    acceleration = readWakeupAcceleration()
    batteryLevel = readLowBatteryLevel()
    sleepTime = readSleepTime()
    print('Acceleration: {}Gs'.format(acceleration))
    print('Low battery level: {}%'.format(batteryLevel))
    print('Sleep time: {}ms'.format(sleepTime))

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Read/write BLERemote settings.',
            epilog = 'If no settings are specified, just displays the current values.')
    parser.add_argument('-a', '--address', type = str, required = True, help = 'the BT address of the remote')
    parser.add_argument('--acceleration', type = float, help = 'the acceleration required to wake the remote, in Gs (default 1.5)')
    parser.add_argument('--lowBattery', type = int, help = 'the battery level at which the remote indicates low battery, in percent (default 20)')
    parser.add_argument('--sleep', type = int, help = 'the time after which the remote goes to sleep, in milliseconds (default 10000)')
    parser.add_argument('--reset', action = 'store_true', help = 'reset (reboot) the remote')
    
    options = parser.parse_args(sys.argv[1:])
    connect(options.address)
    if options.acceleration:
        writeWakeupAcceleration(options.acceleration)
    if options.lowBattery:
        writeLowBatteryLevel(options.lowBattery)
    if options.sleep:
        writeSleepTime(options.sleep)
        
    readValues()
    
    if options.reset:
        reset()

    disconnect()
    
        