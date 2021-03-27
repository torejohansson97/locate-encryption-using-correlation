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

from sdr import *
from targetDevice import *

def main():
	outputfile = '../data/our-data/raw'
	targetDevicePort = '/dev/ttyACM0'
	repetiotion = 10
	numberOfKeys = 5
	key = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	plaintext = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	
	recorder = SDR(outfile=outputfile)
	target = TargetDevice(targetDevicePort)

	target.setChannel()
	target.setPower()
	target.startCarrier()

	target.enterTinyAES()
	target.setRepetition(repetiotion)
	recorder.start()
	for i in range(1,numberOfKeys+1): # 1, 2, 3, 4, 5
		count=0
		start = time.perf_counter()
		dir = '../data/our-data/for_testing/10k_d10_k' + str(i) + '_1avg_10rep'
		key = np.load(dir + '/key.npy')
		plaintext = np.load(dir + '/pt.npy')
		total = plaintext.shape[0]
		
		target.setKey(key)
	
		printProgressBar(0, total, prefix = 'Progress:', suffix = 'Complete', length = 50)
		for text in plaintext:
			
			target.setPlainText(text)
			#recorder.start()
			time.sleep(0.06) # Sleep to prevent noise in encryption
			target.runEncryption()
			
			time.sleep(0.01)
			recorder.blocks_file_sink_0.close()
			raw = np.fromfile(outputfile, dtype='float32')[-130000:] # Cut the crap
			
			raw = raw.reshape(1, len(raw)) # Transpose
			
			if not os.path.exists(dir + '/traces.npy'):
				length = raw.shape[1] 
				traces = np.memmap(dir + '/traces.npy', dtype='float32', mode='w+', shape=(total, length))
				
			traces[count, :] = raw
			count+=1
			printProgressBar(count, total, start)
			os.remove(outputfile)
			recorder.blocks_file_sink_0.open(outputfile)
		
		traces.flush() # Save to disk
		print('Time: ' + str(time.perf_counter() - start))
		#print('Shape: ' + str(traces.shape))
	
	print('\nFinished!')
	target.exitTinyAES()    
	target.stopCarrier()
	print('Total time: ' + str(round(time.perf_counter() - start)/60) + ' min')
	# Clean up and exit
	recorder.stop()
	recorder.wait()
	target.close()

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
