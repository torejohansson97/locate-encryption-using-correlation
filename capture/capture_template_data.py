#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This script is used to capture the data in template_data folder

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
	repetiotion = 2
	numberOfKeys = 50
	key = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	plaintext = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	template=np.load('../correlation/avg_of_one_withzeros.npy')
	losttraces = 0
	
	recorder = SDR(outfile=outputfile)
	target = TargetDevice(targetDevicePort)

	target.setChannel()
	target.setPower()
	target.startCarrier()

	target.enterTinyAES()
	target.setRepetition(repetiotion)
	recorder.start()
	
	dir = '../data/our-data/for_template/100k_d10_k50_1avg_1rep'
	keys = np.load(dir + '/key.npy')
	plaintext = np.load(dir + '/pt.npy')
	total = plaintext.shape[0]
	i = 0
	traceNumber = 0

	printProgressBar(0, total, prefix = 'Progress:', suffix = 'Complete', length = 50)
	for key in keys:
		count=0
		start = time.perf_counter()
		i+=1
		target.setKey(key)
	
		for text in plaintext:
			count+=1
			traceNumber+=1
			printProgressBar(count, total, start)

			target.setPlainText(text)
			while True:
				os.remove(outputfile)
				recorder.blocks_file_sink_0.open(outputfile)
				time.sleep(0.06) # Sleep to prevent noise in encryption
				target.runEncryption()
				
				time.sleep(0.01)
				recorder.blocks_file_sink_0.close()
				raw = np.fromfile(outputfile, dtype='float32')[-120000:]
				encryptionBlock = ct.getEncryptionBlockFromArray(raw, template)
				# If we find less than expected, something went wrong so we plot the result.
				# We then try again.
				if encryptionBlock.shape[0] != repetion:
					print("Hittade " + str(encryptionBlock.shape[0]) + ' block')
					plt.ion()
					plt.show()
					corr = ct.getCorrelation(raw, template)
					meanCorr = np.mean(corr)
					std = np.std(corr)
					envelope = ct.getCorrEnvelopeList(corr)[0]
					triggerLevel = [meanCorr + (std*15)]*len(envelope)
					plt.figure(11)
					plt.plot(envelope)
					plt.plot(triggerLevel)
					plt.draw()
					plt.pause(10)
					plt.close()
					losttraces+=1
				else:
					encryptionBlock = encryptionBlock[0]
					encryptionBlock = encryptionBlock.reshape(1, len(encryptionBlock)) # Transpose
					
					if not os.path.exists(dir + '/traces.npy'):
						length = encryptionBlock.shape[1] 
						traces = np.memmap(dir + '/traces.npy', dtype='float32', mode='w+', shape=(total*numberOfKeys, length))
						
					traces[traceNumber-1, :] = encryptionBlock
					break
		print('Time: ' + str(time.perf_counter() - start) + 'Lost traces: ' + str(losttraces))
		
	traces.flush() # Save to disk
	
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
