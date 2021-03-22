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
	if maxLimit != None:
		max = maxLimit
	else:
		max = np.max(inputArray)
	if minLimit != None:
		min = minLimit
	else:
		min = np.min(inputArray)
	binSize = (max - min) / bins
	binList = [0]*bins
	for value in inputArray:
		if value >= min and value <= max:
			index = int((value-min)//binSize)
			try:
				binList[index] += 1
			except IndexError:
				print("IndexError, index: "+ str(index))
	xAxis = []
	for x in range(bins):
		x = x * binSize
		xAxis.append(x+min)
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
def signOfTraces(trace, template, corr = None):
	try:
		if corr == None:
			corr = getCorrelation(trace, template)
	except ValueError:
		pass
	return np.mean(corr) < 0.49



def getTriggerLevel(trace, template, plotBins=False):
	# Returns trigger level based on correlation amplitudes distributed into bins
	print('Distributing correlation to bins...')
	nrBins = 100
	corr = getCorrelation(trace, template)
	if not signOfTraces(None, None, corr):
		return "No sign of traces"
	amplitudes, q = binDistribution(corr, nrBins, 0.5)
	if plotBins:
		plt.figure(nrBins).canvas.set_window_title('Correlation bins')
		plt.plot(amplitudes, q)

	print("Calculating trigger level...")
	max = amplitudes[nrBins-1]
	margin = nrBins//50-1
	for j in range(nrBins-1, -1, -1):
		mean = np.mean(q[j:len(q)])
		if q[j-1] - q[j] > 0 and q[j-2] - q[j-1] > 0 and q[j] > mean:
			level = amplitudes[j+margin]
			print("Trigger level: "+str(level))
			return level
	return max

def getCorrelation(trace, template):
	#print(len(trace), len(template))
	corr = signal.correlate(trace, template, mode='full', method='auto')
	corr = normMaxMin(corr[len(template):len(trace)])
	return corr

def makeTraces(corr, traceArray, triggerLevel, offset):
	print("Splitting array into traces...")
	traces = np.empty((0,400), float) #creating empty array
	indexes = []
	minDistance = 3
	lastTraceIndex = -10
	i = 0
	while i < len(corr):
		value = corr[i]
		if value > triggerLevel and i - lastTraceIndex >= minDistance:
			startIndex = i - offset
			tempIndex = startIndex
			for j in range(1, minDistance):
				if corr[i+j] > value:
					value = corr[i+j]
					tempIndex = startIndex + j
			temp = traceArray[tempIndex:tempIndex+400]
			temp = np.reshape(temp, (1,400))
			traces = np.append(traces, temp, axis=0)
			lastTraceIndex = tempIndex + offset
			indexes.append(lastTraceIndex)
			i+=4000 # Skip samples of saved trace
		else:
			i+=1
	return traces, indexes

def getTracesFromArray(array, template, triggerLevel, plotCorr=False):
	templ_length = len(template)
	print('Correlating...')
	corr = getCorrelation(array, template)

	if(plotCorr):
		plt.figure(0).canvas.set_window_title('Trace & Correlation')
		plt.plot(range(len(array)), array, range(templ_length, len(array)), corr)
	traces, indexes = makeTraces(corr, array, triggerLevel, 3548)
	return traces, indexes
