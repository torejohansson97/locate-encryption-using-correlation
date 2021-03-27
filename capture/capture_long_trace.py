#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, getopt
import os
import serial
import time
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt

sys.path.append('../correlation')
import correlation_tools as ct

from sdr import *
from targetDevice import *

def main():
	outputfile = '../data/our-data/raw'
	targetDevicePort = '/dev/ttyACM0'
	repetiotion = 50
	numberOfKeys = 5
	key = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	plaintext = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	template=np.load('../correlation/avg1_withzeros.npy')
	
	recorder = SDR(outfile=outputfile)
	target = TargetDevice(targetDevicePort)
	
	target.setChannel()
	target.setPower()
	target.startCarrier()

	recorder.start()
	
	dir = '../data/our-data/for_testing/long_traces/with_setup'
	keys = np.load(dir + '/key.npy')
	plaintext = np.load(dir + '/pt.npy')
	total = plaintext.shape[0]
	
	
	count=0
	start = time.perf_counter()
	for text in plaintext:
		os.remove(outputfile)
		recorder.blocks_file_sink_0.open(outputfile)
		target.enterTinyAES()
		target.setRepetition(repetiotion)
		target.setPlainText(text)
		target.setKey(key)
		target.runEncryption()
		target.exitTinyAES()
		target.printMenu()

		recorder.blocks_file_sink_0.close()

		raw = np.fromfile(outputfile, dtype='float32')
			
		raw = raw.reshape(1, len(raw)) # Transpose
		if not os.path.exists(dir + '/traces_cable.npy'):
			length = raw.shape[1] 
			traces = np.memmap(dir + '/traces_cable.npy', dtype='float32', mode='w+', shape=(total, length))
		if raw.shape[1]<length:	
			traces[count, :] = np.zeros((1,length))
			traces[count, :raw.shape[1]] = raw
		else:	
			traces[count, :] = raw[:1, :length]
			
		#--- Update stuff ---#	
		count+=1
		printProgressBar(count, total, start)
	traces.flush() # Save to disk
	print('Time: ' + str(round((time.perf_counter() - start)/60)) + ' min')
		
	
	# Clean up and exit
	target.stopCarrier()
	recorder.stop()
	recorder.wait()
	target.close()

	print('\nFinished!')

# Print iterations progress
def printProgressBar (iteration, total, startTime):
	length=50
	timeRemaining =	((time.perf_counter()-startTime)/iteration)*(total-iteration)
	percent = round(iteration/total, 1) *100
	filledLength = int(length * iteration // total)
	bar = '█' * filledLength + '-' * (length - filledLength)
	if timeRemaining > 60:	
		print('\rProgress |' + bar + '| ' +  str(percent) + '%, Time Remaining: ' + str(round(timeRemaining/60)), end=' min\r') 
	else:	
		print('\rProgress |' + bar + '| ' +  str(percent) + '%, Time Remaining: ' + str(round(timeRemaining)), end=' sec\r') 
	# Print New Line on Complete
	if iteration == total: 
		print()

if __name__ == "__main__":
   main()
