#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, getopt
import os
import serial
import time
import numpy as np

from capture import *

def main():
    outputfile = '../data/our-data/raw'
    targetDevice = '/dev/ttyACM0'
    repetiotion = 100
    key = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    plaintext = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    count=0
    recorder = capture(outfile=outputfile)
    
    dev = serial.Serial(targetDevice, baudrate=115200, timeout=20)

    setChannel(dev)
    setPower(dev)
    startCarrier(dev)

    enterTinyAES(dev)
    setRepetition(dev, repetiotion)
    
    for i in range(1,4):
        #dir = '../data/our-data/100k_d10_k' + str(i) + '_100avg'
        dir = '../data/our-data/test/k' + str(i)
        key = np.load(dir + '/key.npy')
        plaintext = np.load(dir + '/pt.npy')
        setKey(dev, key)
        for text in plaintext:
            print(str(count))
            setPlainText(dev, text)
            recorder.start()
            runEncryption(dev)
            recorder.stop()
            recorder.wait()
            appendRawtoArray(outputfile, dir + '/traces.npy')
            count+=1
            recorder.blocks_file_sink_0.close()
            os.remove(outputfile)
            recorder.blocks_file_sink_0.open(outputfile)
    
    exitTinyAES(dev)    
    stopCarrier(dev)

    # Clean up and exit
    dev.close()

def appendRawtoArray(rawPath, arrayPath):
    raw = np.fromfile(rawPath, dtype='float32')
    print('Raw length: ' + str(len(raw)))
    raw = raw.reshape(1, len(raw))
    try:
        array = np.load(arrayPath)
        length = array.shape[1]
        diff = length - raw.shape[1]
    
        if diff > 0:
            temp = np.zeros((1, array.shape[1]))
            temp[0, :raw.shape[1]] = raw[0]
            raw = temp
        elif diff < 0:
            raw = raw[:1, 0:length] # Trim the capured to equal length
        
        array = np.append(array, raw, axis=0)

    except FileNotFoundError:
        array = raw
    
    np.save(arrayPath, array)

def enterTinyAES(device):
    device.write(b'n') # Enter tinyAES
    print(device.readline())

def exitTinyAES(device):
    device.write(b'q') # Quit tinyAES
    print(device.readline())

def setChannel(device, channel='0'):
    #print("Set channel")
    device.write(b'a')
    print(device.readline())
    device.write(b'0\r\n')
    print(device.readline())

def setPower(device, power='0'):
    #print("Set pwr")
    device.write(b'p0')
    print(device.readline())
    print(device.readline())

def startCarrier(device):
    device.write(b'c')

def stopCarrier(device):
    device.write(b'e')

def setRepetition(device, repetiotion=2000):
    #print("Set rep")
    device.write(b'n' + str(repetiotion).encode() + b'\r\n')
    print(device.readline())    
    
def setKey(device, key):
    # Assumes i tinyAES mode
    #print("Set key")
    command_line = '%s%s\r\n' % ('k', " ".join(str(char) for char in key))
    device.write(command_line.encode())
    print(device.readline())

def setPlainText(device, text):
    # Assumes i tinyAES mode
    #print("Set PT")
    command_line = '%s%s\r\n' % ('p', " ".join(str(char) for char in text))
    device.write(command_line.encode())
    print(device.readline())
    
def runEncryption(device):
    print("Encrypting...")
    device.write(b'r')
    print(device.read_until(b'Done\r\n'))

if __name__ == "__main__":
   main()