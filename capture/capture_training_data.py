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
	repetiotion = 200
	numberOfKeys = 5
	key = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	plaintext = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	template=np.load('../correlation/avg1_withzeros.npy') #TODO: Välj rätt template
	
	recorder = SDR(outfile=outputfile)
	target = TargetDevice(targetDevicePort)

	target.setChannel()
	target.setPower()
	target.startCarrier()

	target.enterTinyAES()
	target.setRepetition(repetiotion)
	recorder.start()
	
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
				target.runEncryption()
				recorder.blocks_file_sink_0.close()

				raw = np.fromfile(outputfile, dtype='float32')[20000:-2000] #TODO: Behövs detta, tweaka std
				plt.plot(raw)
				plt.show()
				encryptionBlock = ct.getEncryptionBlockFromArray(raw, template) # 5 sigma
				#time.sleep(10)

				if encryptionBlock.shape[0] < 150: #!= repetiotion:
					print("Hittade endast" + str(encryptionBlock.shape[0]) + ' block\n')
					plt.ion()
					plt.show()
					corr = ct.getCorrelation(raw, template)
					meanCorr = np.mean(corr)
					std = np.std(corr)
					envelope = ct.getCorrEnvelopeList(corr)[0]
					triggerLevel = [meanCorr + (std*5)]*len(envelope)
					plt.figure(11)
					plt.plot(envelope)
					plt.plot(triggerLevel)
					plt.draw()
					plt.pause(20)
					plt.close()
				
				else:
					encryptionBlock = encryptionBlock[50:150] # Take the 100 middle block, do this to avoid having delays before and after encryption.
					encryptionBlock = encryptionBlock.reshape(1, len(encryptionBlock)) # Transpose
					avg100 = numpy.average(encryptionBlock, axis=0) # Average
					
					if not os.path.exists(dir + '/traces.npy'):
						length = avg100.shape[1] 
						traces = np.memmap(dir + '/traces.npy', dtype='float32', mode='w+', shape=(total, length))
						
					traces[count, :] = avg100
					break # while-loop breaks if everything went well
				
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

	print('\nFinished!')

# Print iterations progress
def printProgressBar (iteration, total, startTime):
	length=50
	timeRemaining =	((time.perf_counter()-startTime)/iteration)*(total-iteration)
	percent = round(iteration/total, 1) 
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
