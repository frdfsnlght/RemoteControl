#!/usr/bin/env python3

import sys, os, struct, argparse
import bluepy
import bluepy.btle as bt

periph = bt.Peripheral()

uuids = {
    'service': bt.UUID('1234'),
    'button': bt.UUID('0001')
}

characteristics = {}


def connect(address):

    class Delegate(bt.DefaultDelegate):
        def handleNotification(self, cHandle, data):
            handleNotification(cHandle, data)
        
    delegate = Delegate()

    try:
        periph.connect(address, bt.ADDR_TYPE_RANDOM)
        service = periph.getServiceByUUID(uuids['service'])
        chars = service.getCharacteristics()

        characteristics['button'] = next((c for c in chars if c.uuid == uuids['button']), None)
        # set up notifications
        notify = struct.pack('<bb', 0x01, 0x00)
        periph.writeCharacteristic(characteristics['button'].getHandle() + 1, notify)
        periph.withDelegate(delegate)

        print('Connected')
    except bt.BTLEDisconnectError:
        print('Unable to connect. Is the remote on the charger?')
        sys.exit(1)
            
def disconnect():
    periph.disconnect()
    characteristics.clear()
    print('Disconnected')



def handleNotification(cHandle, data):
    if cHandle == characteristics['button'].getHandle():
        handleButton(data)

def handleButton(data):
    data = struct.unpack('BB', data)
    button = hex(data[1])
    state = 'down' if data[0] == 1 else 'up'
    print('{}: {}'.format(button, state))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Receive and display button notifications.')
    parser.add_argument('-a', '--address', type = str, required = True, help = 'the BT address of the remote')
    
    options = parser.parse_args(sys.argv[1:])
    connect(options.address)

    print('Press CTRL-C to stop')
    try:
        while True:
            periph.waitForNotifications(1)
    except KeyboardInterrupt:
        pass

    disconnect()
    
        