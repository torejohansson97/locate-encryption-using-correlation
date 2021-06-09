# Simon Weideskog and Tore Johansson
# Last edited: 2021-06-09
"""
Module with useful functions for locating encryption blocks using correlation.
Test code is in test_suite.py!
"""
import numpy as np
from scipy import signal, fftpack
import os
import matplotlib.pyplot as plt

"""
Following constants depends on encryption implementation
and need to be adjusted for different kinds of targets.
"""
BLOCK_LENGTH = 4100
ROUND_LENGTH = 400
FIRSTROUND_START = 800
LASTROUND_START = 3720

def getEncryptionBlocksFromArray(traceArray, template, padding=200, triggerMultiplier=10, normalize=True):
	"""
	Returns an array with all found encryption blocks in a recorded trace (traceArray).
	The template for correlation, padding around the outputted blocks and the
	chosen trigger multiplier must be provided for this function.

	The function 'plotEnvelopeWithTrigger' can be called before this function
	in order to chose trigger multiplier visually.
	"""
	corr = getCorrelation(traceArray, template, True)
	corrEnvelopeList = getCorrEnvelopeList(corr, normalize, traceArray)
	indices = getBlockIndicesFromEnvelope(corr, corrEnvelopeList, 0, triggerMultiplier)
	return cutEncryptionBlocks(traceArray, indices, padding)

def average(traces):
	"""
	Combining all traces from the 2-dimensional input array
	into an average trace, sample by sample.
	"""
	return np.mean(traces, axis=0)

def normMaxMin(inputArray):
	"""
	Implementation of the min-max normalization. Returns normalized version of
	the input array.
	"""
	tempArray = np.array(inputArray.copy())
	max = np.max(tempArray)
	min = np.min(tempArray)
	tempArray[:] = (tempArray - min) / (max - min)
	return tempArray

def getBlockIndicesFromEnvelope(corr, envelopeList, offset, triggerMultiplier=10):
	"""
	Returns indices of where encryption blocks are located, based on the
	envelope list and the chosen trigger multiplier (here multiplied with the
	standard deviation of the correlation array).
	"""
	meanCorr = np.mean(corr)
	std = np.std(corr)
	triggerLevel = meanCorr + (std*triggerMultiplier)
	indices = []
	amps = envelopeList[0]
	for i in range(1,len(amps)-1):
		if amps[i] > triggerLevel and amps[i] > amps[i-1] and amps[i] > amps[i+1]: # Check if amp is bigger than half the max value and a local maxima
			indices.append(envelopeList[1][i]+offset)
	return indices

def getBlockStatsFromEnvelope(corr, envelopeList, offset, triggerMultiplier=10):
	"""
	Returns statistics of found encryption blocks
	instead of indices. Used for testing.
	"""
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
	try:
		peakVariance = np.var(peaks)
		peakMean = sum(peaks)/len(peaks)
	except ZeroDivisionError:
		peakMean = None
	return numIndices, peakMean, peakVariance, meanCorr, std

def getCorrEnvelopeList(corr, normalize, trace=[], segmentLength=600, longSegment=8000):
	"""
	Returns envelope array based on segments of the correlation array
	with both maximum value within segment and indices of the maximum values.

	Can also perform normalization if 'normalize' is set to True.
	See report for details.
	"""
	envelope = [[],[]]
	traceMaxAbs = np.max(np.abs(trace))
	startIndex = 0
	stopLength = segmentLength
	length = len(corr)
	while startIndex < length and stopLength == segmentLength:
		normFactor = 1
		if startIndex + segmentLength > length:
			stopLength = length - 1 - startIndex
		segment = corr[startIndex:startIndex+stopLength]
		index = startIndex + np.argmax(segment)
		# Normalization code:
		if normalize and len(trace) != 0:
			longSegmentStart = startIndex - int(longSegment/2) + stopLength
			if longSegmentStart < 0:
				longSegmentStart = 0
			longSegmentStop = longSegmentStart+longSegment
			if longSegmentStart + longSegment > len(trace):
				longSegmentStop = len(trace)-1
			longSegmentMax = np.max(np.abs(trace[longSegmentStart:longSegmentStop]))
			if longSegmentMax == 0:
				longSegmentMax = traceMaxAbs
			normFactor = 1/(longSegmentMax*100)
			biggest = (corr[index]**5)*normFactor
		else:
			biggest = corr[index]

		envelope[0].append(biggest)
		envelope[1].append(index)
		startIndex+=segmentLength
	return envelope

def cutEncryptionBlocks(traceArray, indices, padding):
	"""
	Returns array with all extracted encryption blocks from the recorded trace
	array without any other modifications to the data. The blocks are padded
	according to the argument 'padding'.
	"""
	blockSize = BLOCK_LENGTH+2*padding
	blocks = np.empty((0,blockSize))
	for i in indices:
		temp = traceArray[i-padding:i-padding+blockSize]
		if len(temp) < blockSize:
			continue
		temp = np.reshape(temp, (1,blockSize))
		blocks = np.append(blocks, temp, axis=0)
	return blocks

def getCorrelation(trace, template, norm=True):
	"""
	Returns cross correlation between recorded trace and template, as an array
	with the same length as the trace.
	"""
	corr = signal.correlate(trace, template, mode='full', method='auto')
	corr = corr[len(template):len(trace)+len(template)]
	if norm:
		corr = normMaxMin(corr)
	return corr

def plotEnvelopeWithTrigger(traceArray, template, normalize=False):
	"""
	Used for visualizing the envelope array together with the resulting
	trigger level for 3 different examples of trigger multiplier. This
	is useful when choosing trigger multiplier.
	"""
	corr = getCorrelation(traceArray, template)
	meanCorr = np.mean(corr)
	std = np.std(corr)
	envelope = getCorrEnvelopeList(corr, normalize, traceArray)[0]
	#plotFrequencies(envelope)
	triggerLevel1 = [meanCorr + (std*5)]*len(envelope)
	triggerLevel2 = [meanCorr + (std*10)]*len(envelope)
	triggerLevel3 = [meanCorr + (std*15)]*len(envelope)
	plt.rcParams["figure.figsize"] = (8,3)
	plt.gcf().subplots_adjust(bottom=0.15)
	plt.plot(envelope, label='Envelope')
	plt.plot(triggerLevel3, label='triggerMultiplier = 15')
	plt.plot(triggerLevel2, label='triggerMultiplier = 10')
	plt.plot(triggerLevel1, label='triggerMultiplier = 5')
	plt.xlabel('Segment number')
	plt.ylabel('Amplitude')
	plt.legend(loc="upper right")
	plt.show()
