#!/usr/bin/python

import sys, os, struct, argparser
import bluepy.btle as bt


serviceUUID = bt.UUID('1234')
buttonUUID = bt.UUID('0001')
ledsUUID = bt.UUID('0002')
chargingUUID = bt.UUID('0003')
batteryLevelUUID = bt.UUID('0004')
resetUUID = bt.UUID('0099')



if __name__ == 'main':
    argparse.ArgumentParser(description='Read/write BLERemote settings.')
    
