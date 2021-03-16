#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, getopt
import serial

from capture import *

def main():
    outputfile='out'
    targetDevice = '/dev/ttyACM0'
    repetiotion = 2000
    key = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    text = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    recorder = capture(outfile=outputfile)
    
    dev = serial.Serial(targetDevice, baudrate=115200, timeout=1)
    setChannel(dev)
    setPower(dev)
    startCarrier(dev)

    writeToSerial(dev, 'n') # Enter tinyAES
    
    setRepetition(dev)
    setKey(dev, key)
    setPlainText(dev, text)
    
    recorder.start()

    writeToSerial(dev, 'r') # Run encryption
    writeToSerial(dev, 'q') # Quit tinyAES
    stopCarrier(dev)

    # Clean up and exit
    recorder.stop()
    recorder.wait()
    dev.close()

def writeToSerial(device, data):
    device.write(data.encode())
    print(device.readline().decode().strip())

def setChannel(device, channel='0'):
    writeToSerial(device, 'a')
    writeToSerial(device, channel)

def setPower(device, power='0'):
    writeToSerial(device, 'p')
    writeToSerial(device, power)

def startCarrier(device):
    writeToSerial(device, 'c')

def stopCarrier(device):
    writeToSerial(device, 'e')

def setRepetition(device, repetiotion='2000'):
    writeToSerial(device, 'n')
    writeToSerial(device, repetiotion)

def setKey(device, key):
    # Assumes i tinyAES mode
    writeToSerial(device, 'k')
    writeToSerial(device, " ".join(str(char) for char in key))

def setPlainText(device, text):
    # Assumes i tinyAES mode
    writeToSerial(device, 'p')
    writeToSerial(device, " ".join(str(char) for char in text))

if __name__ == "__main__":
   main()