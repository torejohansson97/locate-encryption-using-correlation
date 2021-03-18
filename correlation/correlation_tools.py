"""
Module with useful functions for trace identification using correlation.
Test code is in test_suite.py!
"""
import numpy as np
from scipy import signal
import os
import matplotlib.pyplot as plt

TEMPLATE_LENGTH = 4100

def average(traces):
	return np.mean(traces, axis=0)	# all the traces to one

def averageOfOne(trace, startIndex):
	return trace[startIndex:startIndex+TEMPLATE_LENGTH]

def normMaxMin(inputArray):
	max = np.max(inputArray)
	min = np.min(inputArray)
	return np.array([(x - min) / (max - min) for x in inputArray])

def binDistribution(inputArray, bins, minLimit=None, maxLimit=None):
	max = np.max(inputArray)
	if maxLimit != None and max > maxLimit:
		max = maxLimit
	min = np.min(inputArray)
	if minLimit != None and min < minLimit:
		min = minLimit
	binSize = (max - min) / bins
	binList = [0]*bins
	for value in inputArray:
		index = int((value-min)//binSize)
		try:
			binList[index] += 1
		except IndexError:
			print("IndexError, index: "+ str(index))
	xAxis = []
	for x in range(bins):
		x = x * binSize
		x += min
		xAxis.append(x)
	return (xAxis, binList)
"""
def filterArray(array, distanceBetweenPeeks=4300, highPassCutoff=0.01,lowPassCutoff=0.1):
	ny = 0.5*distanceBetweenPeeks
    low = lowPassCutoff/ny
    high = highcut/ny
    b, a = signal.butter(5, [low, high], btype='band')
	y = signal.lfilter(b, a)
	return signal.filtfilt(b, a, array)
"""

def getTriggerLevel(amplitudes, quantities, ampDiff = 0.2):
	# Returns trigger level based on correlation amplitudes distributed into bins

	print("Calculating trigger level...")
	nrBins = len(amplitudes)
	max = amplitudes[nrBins-1]
	margin = nrBins//50
	maxCorrPeakQuantity = 0
	for j in range(nrBins):
		i = j + 1
		quantity = quantities[nrBins-i]
		amplitude = amplitudes[len(amplitudes)-i]
		if quantity > maxCorrPeakQuantity:
			maxCorrPeakQuantity = quantity
		if amplitudes[nrBins-i] < max - ampDiff / 2:
			break
	for j in range(nrBins):
		i = j + 1
		if quantities[nrBins-i] > maxCorrPeakQuantity:
			return amplitudes[nrBins - i + margin]
	return max

def makeTraces(corr, traceArray, trigger, offset):
	print("Splitting array into traces...")
	traces = np.empty((0,400), float) #creating empty array
	indexes = []
	minDistance = 10
	lastTraceIndex = -10
	for i in range(len(corr)):
		value = corr[i]
		if value > trigger and i - lastTraceIndex >= minDistance:
			startIndex = i - offset
			for j in range(1, minDistance):
				if corr[i+j] > value:
					value = corr[i+j]
					startIndex += j
					break
			temp = traceArray[startIndex:startIndex+400]
			temp = np.reshape(temp, (1,400))
			traces = np.append(traces, temp, axis=0)
			lastTraceIndex = startIndex + offset
			indexes.append(startIndex)
	return traces, indexes

def getTracesFromArray(array, template, plotCorr=False):
	templ_length = len(template)
	print('Correlating...')
	corr = signal.correlate(array, template, mode='full', method='auto')
	corr = normMaxMin(corr[templ_length:len(array)])
	print('Distributing to bins...')
	corrAmplitudes, quantities = binDistribution(corr, 100)
	if(plotCorr):
		plt.figure(0).canvas.set_window_title('Trace & Correlation')
		plt.plot(range(len(array)), array, range(templ_length, len(array)), corr)
		plt.figure(1).canvas.set_window_title('Correlation bins')
		plt.plot(corrAmplitudes, quantities)
	traces, indexes = makeTraces(corr, array, getTriggerLevel(corrAmplitudes, quantities, 0.25), 3548)
	return traces, indexes
