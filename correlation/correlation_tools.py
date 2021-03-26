"""
Module with useful functions for trace identification using correlation.
Test code is in test_suite.py!
"""
import numpy as np
from scipy import signal, fftpack
import os
import matplotlib.pyplot as plt

TEMPLATE_LENGTH = 4100

def getTracesFromArray(traceArray, template):
	corr = getCorrelation(traceArray, template, False)
	corrEnvelopeList = getCorrEnvelopeList(corr)
	indices = getTraceIndicesFromEnvelope(corr, corrEnvelopeList, 800)
	return cutTracesWithIndices(traceArray, indices)

def getEncryptionBlockFromArray(traceArray, template, padding=200):
	corr = getCorrelation(traceArray, template, False)
	corrEnvelopeList = getCorrEnvelopeList(corr)
	indices = getTraceIndicesFromEnvelope(corr, corrEnvelopeList, 0)
	return cutEncryptionBlocks(traceArray, indices, padding)

def average(traces):
	return np.mean(traces, axis=0)	# all the traces to one

def averageOfOne(trace, startIndex):
	return trace[startIndex:startIndex+TEMPLATE_LENGTH]

def normMaxMin(inputArray):
	max = np.max(inputArray)
	min = np.min(inputArray)
	return np.array([(x - min) / (max - min) for x in inputArray])

def getTraceIndicesFromEnvelope(corr, envelopeList, offset, triggerMultiplier=10):
	#print('Getting indexes of correlations peaks...')
	meanCorr = np.mean(corr)
	std = np.std(corr)
	triggerLevel = meanCorr + (std*triggerMultiplier)
	indices = []
	amps = envelopeList[0]
	for i in range(1,len(amps)-1):
		if amps[i] > triggerLevel and amps[i] > amps[i-1] and amps[i] > amps[i+1]: # Check if amp is bigger than half the max value and a local maxima
			indices.append(envelopeList[1][i]+offset)
	return indices

def getTraceStatsFromEnvelope(corr, envelopeList, offset, triggerMultiplier=10):
	#print('Getting indexes of correlations peaks...')
	meanCorr = np.mean(corr)
	std = np.std(corr)
	triggerLevel = meanCorr + (std*triggerMultiplier)
	numIndices = 0
	peaks = []
	amps = envelopeList[0]
	for i in range(1,len(amps)-1):
		if amps[i] > triggerLevel and amps[i] > amps[i-1] and amps[i] > amps[i+1]: # Check if amp is bigger than half the max value and a local maxima
			numIndices+=1
			peaks.append(amps[i])
	peakVariance = np.var(peaks)
	peakMean = np.mean(peaks)
	return numIndices, peakMean, peakVariance, meanCorr, std

def getCorrEnvelopeList(corr, segmentLength=400):
	#print('Saving max amplitudes in segments and their indices to envelope list... (Segment length: ' +str(segmentLength)+')')
	envelope = [[],[]]
	startIndex = 0
	stop = segmentLength
	length = len(corr)
	while startIndex < length and stop == segmentLength:
		if startIndex + segmentLength > length:
			index = startIndex + np.argmax(corr[startIndex:len(corr)])
			biggest = corr[index]
			stop = length - 1 - startIndex
		else:
			index = startIndex + np.argmax(corr[startIndex:startIndex+segmentLength])
			biggest = corr[index]
		envelope[0].append(biggest)
		envelope[1].append(index)
		startIndex+=segmentLength
	return envelope

def getCorrEnvelope(corr, segmentLength=400):
	envelope = np.empty((2,corr.shape[0]))
	startIndex = 0
	stop = segmentLength
	length = len(corr)
	while startIndex < length and stop == segmentLength:
		if startIndex + segmentLength > length:
			index = startIndex + np.argmax(corr[startIndex:len(corr)])
			biggest = corr[index]
			stop = length - 1 - startIndex
		else:
			index = startIndex + np.argmax(corr[startIndex:startIndex+segmentLength])
			biggest = corr[index]
		#envelope[startIndex:startIndex+stop]=np.linspace(envelope[startIndex-1],biggest, num=stop)
		envelope[0][startIndex:startIndex+stop]=np.array(([biggest]*stop))
		envelope[1][startIndex:startIndex+stop]=np.array(([index]*stop))
		startIndex+=segmentLength
	return envelope

def cutTracesWithIndices(traceArray, indices):
	#print('Splitting array into traces...')
	traces = np.empty((0,400))
	for i in indices:
		temp = traceArray[i:i+400]
		temp = np.reshape(temp, (1,400))
		traces = np.append(traces, temp, axis=0)
	return traces

def cutEncryptionBlocks(traceArray, indices, padding):
	#print('Splitting array into blocks...')
	blockSize = 4100+2*padding
	blocks = np.empty((0,blockSize))
	for i in indices:
		temp = traceArray[i-padding:i-padding+blockSize]
		temp = np.reshape(temp, (1,blockSize))
		blocks = np.append(blocks, temp, axis=0)
	return blocks

def signOfTraces(trace, template, corr = None):
	try:
		if corr == None:
			corr = getCorrelation(trace, template)
	except ValueError:
		pass
	return np.mean(corr) < 0.49

def getCorrelation(trace, template, norm=True):
	corr = signal.correlate(trace, template, mode='full', method='auto')
	corr = corr[len(template):len(trace)]
	if norm:
		corr = normMaxMin(corr)
	return corr

def plotEnvelopeWithTrigger(traceArray, template):
	corr = getCorrelation(traceArray, template)
	meanCorr = np.mean(corr)
	std = np.std(corr)
	envelope = getCorrEnvelopeList(corr)[0]
	triggerLevel1 = [meanCorr + (std*5)]*len(envelope)
	triggerLevel2 = [meanCorr + (std*10)]*len(envelope)
	triggerLevel3 = [meanCorr + (std*15)]*len(envelope)
	plt.plot(envelope, label='Envelope')
	plt.plot(triggerLevel3, label='triggerMultiplier = 15')
	plt.plot(triggerLevel2, label='triggerMultiplier = 10')
	plt.plot(triggerLevel1, label='triggerMultiplier = 5')
	plt.legend(loc="upper left")
	plt.show()

""" Old code: """
"""
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

def plotFrequencies(array):
	N = len(array) # Number of samples
	f_s = 5000000 # Sample frequency of Software defined radio
	yf = fftpack.fft(array)
	xf = fftpack.fftfreq(N) * f_s
	fig, ax = plt.subplots()
	ax.plot(xf, np.abs(yf))

def _butterBandpassFilter(array, lowcut, highcut, f_s, order=5):
    nyq = 0.5 * f_s
    low = lowcut / nyq
    high = highcut / nyq
    sos = signal.butter(order, [low, high], analog=False, btype='band', output='sos')
    y = signal.sosfilt(sos, array)
    return y

def filterArray(array, distanceBetweenPeeks=4370):
	#plotFrequencies(array)
	f_s = 5000000
	t_s = 1/f_s
	f_enc = 1 / (distanceBetweenPeeks*t_s)
	low = f_enc * 0.1
	high = f_enc * 10
	y = _butterBandpassFilter(array, low, high, f_s, 10)
	#plotFrequencies(y)
	return y

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
"""
