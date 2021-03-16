#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, getopt
import serial

from capture import *

def main():
    outputfile=''
    radioaddr=''
    targetdev=''
    # repetiotion
    # plain text
    # key
    # parseArguments()

    recorder = capture()
    
    dev = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=1)
    writeToSerial(dev, 'a')
    writeToSerial(dev, '0')
    writeToSerial(dev, 'p')
    writeToSerial(dev, '1')
    #writeToSerial(dev, 's')
    writeToSerial(dev, 'c')
    writeToSerial(dev, 'n')
    
    writeToSerial(dev, 'n')
    writeToSerial(dev, '2000 ')
    writeToSerial(dev, 'k')
    writeToSerial(dev, '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ')
    writeToSerial(dev, 'p')
    writeToSerial(dev, '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ')
    #writeToSerial(dev, '16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 ')
    
    recorder.start()

    writeToSerial(dev, 'r')
    writeToSerial(dev, 'q')
    writeToSerial(dev, 'e')

    # Clean up and exit
    recorder.stop()
    recorder.wait()
    dev.close()

def writeToSerial(device, data):
    device.write(data.encode())
    print(device.readline().decode().strip())

def parseArguments():
    try:
      opts, args = getopt.getopt(argv,"ho:r",["ofile=", "raddr="])
    except getopt.GetoptError:
        print('test.py -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -o <outputfile>')
            sys.exit()
        elif opt in ("-o", "--ofile"):
            outputfile = arg

if __name__ == "__main__":
   main()

# Navigera till tinyAES, gör inställningar
# Starta en capture
# Starta kryptering, vänta på 'done'
# Avsluta