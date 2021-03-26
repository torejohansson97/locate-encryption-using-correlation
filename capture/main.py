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
	repetiotion = 100
	key = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	plaintext = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	template = np.load('../correlation/avg_of_one_withzeros.npy')
	
	recorder = capture(outfile=outputfile)
	
	dev = serial.Serial(targetDevice, baudrate=115200, timeout=20)

	setChannel(dev)
	setPower(dev)
	startCarrier(dev)

	enterTinyAES(dev)
	setRepetition(dev, repetiotion)
	start = time.perf_counter()
	for i in range(1,4): # 1, 2, 3
		count=0
		#dir = '../data/our-data/100k_d10_k' + str(i) + '_100avg'
		dir = '../data/our-data/test/k' + str(i)
		key = np.load(dir + '/key.npy')
		plaintext = np.load(dir + '/pt.npy')
		setKey(dev, key)
		printProgressBar(0, plaintext.shape[0], prefix = 'Progress:', suffix = 'Complete', length = 50)
		for text in plaintext:
			count+=1
			printProgressBar(count, plaintext.shape[0], prefix = 'Key ' + str(i) + '/3 Progress:', suffix = 'Complete', length = 50)
			setPlainText(dev, text)
			recorder.start()
			time.sleep(0.07) # Sleep to prevent noise in encryption
			runEncryption(dev)
			#recorder.stop()
			recorder.wait()
			#appendRawtoArray(outputfile, dir + '/traces.npy')
			raw = np.fromfile(outputfile, dtype='float32')[340000:] # Cut the crap
		 

			#TODO: Avraging of the 100 repetitions in raw, after this the raw array should be about 1/100 in length and contain one 100avg trace. The following lines saves it to the array on disk.
			raw = extractTraces(raw, template, 0.73) # 0.73 bestämt av experiment
			print("Number of traces found: " + str(raw.shape[0]))
			raw = ct.average(raw)
			raw = raw.reshape(1, len(raw)) # Transpose
			
			if not os.path.exists(dir + '/traces.npy'):
				length = raw.shape[1] 
				traces = np.memmap(dir + '/traces.npy', dtype='float32', mode='w+', shape=(10, length))
				traces[0, :] = raw # First row is raw

			else:
				diff = length - raw.shape[1]
				if diff > 0:
					temp = np.zeros((1, traces.shape[1]))
					temp[0, :raw.shape[1]] = raw[0]
					raw = temp
				elif diff < 0:
					raw = raw[:1, 0:length] # Trim the capured to equal length
				
				traces[count-1, :] = raw
			
			recorder.blocks_file_sink_0.close()
			os.remove(outputfile)
			recorder.blocks_file_sink_0.open(outputfile)
		
		traces.flush() # Save to disk
		print('Time: ' + str(time.perf_counter() - start))
		print('Shape: ' + str(traces.shape))
	
	print('\nFinished!')
	exitTinyAES(dev)    
	stopCarrier(dev)
	print('Total time: ' + str(time.perf_counter() - start))
	# Clean up and exit
	dev.close()

def appendRawtoArray(rawPath, arrayPath):
	raw = np.fromfile(rawPath, dtype='float32')
	#print('Raw length: ' + str(len(raw)))
	raw = raw.reshape(1, len(raw))
	try:
		array = np.load(arrayPath, mmap_mode='r+', allow_pickle=True)
		length = array.shape[1]
		diff = length - raw.shape[1]
	
		if diff > 0:
			temp = np.zeros((1, array.shape[1]))
			temp[0, :raw.shape[1]] = raw[0]
			raw = temp
		elif diff < 0:
			raw = raw[:1, 0:length] # Trim the capured to equal length
		
		array = np.append(array, raw[480000:], axis=0)

	except FileNotFoundError:
		#array = raw
		a = np.memmap(arrayPath, dtype='float32', mode='w+', shape=(100000,(raw.shape[1] - 480000)))
		a = np.append(a, raw[480000:raw.shape[1]], axis=0)
	
	#np.save(arrayPath, array)
	

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
	#print(device.readline())
	device.readline()

def setPlainText(device, text):
	# Assumes i tinyAES mode
	#print("Set PT")
	command_line = '%s%s\r\n' % ('p', " ".join(str(char) for char in text))
	device.write(command_line.encode())
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
