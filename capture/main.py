#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, getopt
import serial
import time

from capture import *

def main():
    outputfile='out'
    targetDevice = '/dev/ttyACM0'
    repetiotion = 100
    key = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,23,0]
    text = [0,0,0,0,0,0,0,0,0,25,0,0,0,0,0,0]

    recorder = capture(outfile=outputfile)
    
    dev = serial.Serial(targetDevice, baudrate=115200, timeout=20)

    setChannel(dev)
    setPower(dev)
    startCarrier(dev)

    enterTinyAES(dev)
    setRepetition(dev, repetiotion)
    setKey(dev, key)
    setPlainText(dev, text)
    
    recorder.start()

    runEncryption(dev)
    
    exitTinyAES(dev)    
    stopCarrier(dev)

    # Clean up and exit
    recorder.stop()
    recorder.wait()
    dev.close()

def enterTinyAES(device):
    device.write(b'n') # Enter tinyAES
    print(device.readline())

def exitTinyAES(device):
    device.write(b'q') # Quit tinyAES
    print(device.readline())

def setChannel(device, channel='0'):
    device.write(b'a')
    print(device.readline())
    device.write(b'0\r\n')
    print(device.readline())

def setPower(device, power='0'):
    device.write(b'p0')
    print(device.readline())
    print(device.readline())

def startCarrier(device):
    device.write(b'c')

def stopCarrier(device):
    device.write(b'e')

def setRepetition(device, repetiotion=2000):
    device.write(b'n2000\r\n')
    print(device.readline())    
    
def setKey(device, key):
    # Assumes i tinyAES mode
    command_line = '%s%s\r\n' % ('k', " ".join(str(char) for char in key))
    device.write(command_line.encode())
    print(device.readline())

def setPlainText(device, text):
    # Assumes i tinyAES mode
    command_line = '%s%s\r\n' % ('p', " ".join(str(char) for char in text))
    device.write(command_line.encode())
    print(device.readline())
    
def runEncryption(device):
    print("Encrypting...")
    device.write(b'r')
    print(device.readline())

if __name__ == "__main__":
   main()