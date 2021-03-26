#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, getopt
import os
import serial
import time
import numpy as np
from scipy import signal

sys.path.append('../correlation')
import correlation_tools as ct

from capture import *

def main():
	outputfile = '../data/our-data/raw'
	targetDevice = '/dev/ttyACM0'
	repetiotion = 10
	numberOfKeys = 5
	key = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	plaintext = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	
	recorder = capture(outfile=outputfile)
	
	dev = serial.Serial(targetDevice, baudrate=115200, timeout=10)

	setChannel(dev)
	setPower(dev)
	startCarrier(dev)

	enterTinyAES(dev)
	setRepetition(dev, repetiotion)
	recorder.start()
	for i in range(1,numberOfKeys+1): # 1, 2, 3, 4, 5
		count=0
		start = time.perf_counter()
		dir = '../data/our-data/for_testing/10k_d10_k' + str(i) + '_1avg_10rep'
		key = np.load(dir + '/key.npy')
		plaintext = np.load(dir + '/pt.npy')
		total = plaintext.shape[0]
		
		setKey(dev, key)
	
		printProgressBar(0, total, prefix = 'Progress:', suffix = 'Complete', length = 50)
		for text in plaintext:
			count+=1
			eta = ((time.perf_counter()-start)/count)*(total-count)
			if eta > 60:
				printProgressBar(count, total, prefix = 'Key ' + str(i) + '/' + str(numberOfKeys) + ' Progress:', suffix = 'Complete, Time Remaining: '+ str(round((eta/60)))+' min', length = 50)

			else:
				printProgressBar(count, total, prefix = 'Key ' + str(i) + '/' + str(numberOfKeys) + ' Progress:', suffix = 'Complete, Time Reamining: '+ str(round(eta))+' sec', length = 50)

			setPlainText(dev, text)
			#recorder.start()
			time.sleep(0.06) # Sleep to prevent noise in encryption
			runEncryption(dev)
			
			time.sleep(0.01)
			recorder.blocks_file_sink_0.close()
			raw = np.fromfile(outputfile, dtype='float32')[-130000:] # Cut the crap
			
			raw = raw.reshape(1, len(raw)) # Transpose
			
			if not os.path.exists(dir + '/traces.npy'):
				length = raw.shape[1] 
				traces = np.memmap(dir + '/traces.npy', dtype='float32', mode='w+', shape=(total, length))
				
			traces[count-1, :] = raw
			
			os.remove(outputfile)
			recorder.blocks_file_sink_0.open(outputfile)
		
		traces.flush() # Save to disk
		print('Time: ' + str(time.perf_counter() - start))
		#print('Shape: ' + str(traces.shape))
	
	print('\nFinished!')
	exitTinyAES(dev)    
	stopCarrier(dev)
	print('Total time: ' + str(round(time.perf_counter() - start)/60) + ' min')
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
	command_line = '%s%s\r' % ('k', " ".join(str(char) for char in key))
	device.write(command_line.encode())
	#print(device.readline())
	device.readline()

def setPlainText(device, text):
	# Assumes i tinyAES mode
	#print("\nSet PT")
	command_line = '%s%s\r' % ('p', " ".join(str(char) for char in text))
	device.write(command_line.encode())
	#print(command_line.encode())
	#print(device.readline())
	device.readline()
	
	
def runEncryption(device):
	#print("Encrypting...")
	device.write(b'r')
	#print(device.read_until(b'Done\r\n'))
	device.read_until(b'Done\r\n')

def extractTraces(array, template, triggerLevel):
	templ_length = len(template)
	print('Correlating...')
	corr = signal.correlate(array, template, mode='full', method='auto')
	corr = ct.normMaxMin(corr[templ_length:len(array)])
	traces, indexes = ct.makeTraces(corr, array, triggerLevel, 3548)
	
	return traces

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
	"""
	Call in a loop to create terminal progress bar
	@params:
		iteration   - Required  : current iteration (Int)
		total       - Required  : total iterations (Int)
		prefix      - Optional  : prefix string (Str)
		suffix      - Optional  : suffix string (Str)
		decimals    - Optional  : positive number of decimals in percent complete (Int)
		length      - Optional  : character length of bar (Int)
		fill        - Optional  : bar fill character (Str)
		printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
	"""
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(length * iteration // total)
	bar = fill * filledLength + '-' * (length - filledLength)
	print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
	# Print New Line on Complete
	if iteration == total: 
		print()

if __name__ == "__main__":
   main()
