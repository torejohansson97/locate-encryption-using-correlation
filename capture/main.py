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
    
    # dev = serial.Serial(targetdev)
   # dev.write('a0p1cnn' + '2000')

    recorder.start()

    #dev.write() # Start encryption
    #dev.read_until(terminator='done\r\n') # 'done'?
    
    # Clean up and exit
    recorder.stop()
    recorder.wait()
    dev.close()
    
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