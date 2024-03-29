#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This script is used to capture the data in training_data folder

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
	repetiotion = 110
	numberOfKeys = 5
	key = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	plaintext = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	template=np.load('../data/our-data/templates/avg100.npy')
	
	recorder = SDR(outfile=outputfile)
	target = TargetDevice(targetDevicePort)

	target.setChannel()
	target.setPower()
	target.startCarrier()

	target.enterTinyAES()
	target.setRepetition(repetiotion)
	recorder.start()
	
	beginingOfTime = time.perf_counter()

	for i in range(1,numberOfKeys+1):
		dir = '../data/our-data/for_training/100k_d10_k' + str(i) + '_100avg'
		keys = np.load(dir + '/key.npy')
		plaintext = np.load(dir + '/pt.npy')
		total = plaintext.shape[0]
		target.setKey(key)
		
		count=0
		start = time.perf_counter()
		for text in plaintext:
			target.setPlainText(text)
			while True:
				os.remove(outputfile)
				recorder.blocks_file_sink_0.open(outputfile)
				time.sleep(0.005) # Make sure SDR is ready before encryption starts.
				target.runEncryption()
				recorder.blocks_file_sink_0.close()

				raw = np.fromfile(outputfile, dtype='float32')
				try:
					# Use our correlation method to extract encrytionblocks from
					# the trace.
					encryptionBlock = ct.getEncryptionBlockFromArray(raw, template, 200, 9)

					if encryptionBlock.shape[0] == repetiotion:
						# Take the 100 middle block. Do this to avoid the need of
						# having delays before and after encryption start and to 
						# prevent loss of encryption blocks due to timing errors.
						encryptionBlock = encryptionBlock[5:105] 
						avg100 = np.average(encryptionBlock, axis=0) # Average
						avg100 = avg100.reshape(1, len(avg100)) # Transpose
						
						if not os.path.exists(dir + '/traces.npy'):
							length = avg100.shape[1] 
							traces = np.memmap(dir + '/traces.npy', dtype='float32', mode='w+', shape=(total, length))
							
						traces[count, :] = avg100
						break # while-loop breaks if everything went well
				except ValueError:
					pass
				
			#--- Update stuff ---#	
			count+=1
			printProgressBar(count, total, start)
		traces.flush() # Save to disk
		print('Time: ' + str(round((time.perf_counter() - start)/60)) + ' min')
		
	
	# Clean up and exit
	target.exitTinyAES()   
	target.stopCarrier()
	recorder.stop()
	recorder.wait()
	target.close()

	print('\nFinished! Total time: ' + str(round((time.perf_counter() - beginingOfTime)/60)) + ' min')

# Print iterations progress
def printProgressBar (iteration, total, startTime):
	length=50
	timeRemaining =	((time.perf_counter()-startTime)/iteration)*(total-iteration)
	percent = round((iteration/total) *100)
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
