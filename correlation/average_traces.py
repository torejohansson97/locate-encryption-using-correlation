import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import os

ROOTDIR = '../data/ff-em-sca-data'

TEMPLATE_LENGTH = 4100

def combine():
	avg = np.empty((0,400), float) #creating empty array
	print('Loading files...')
	for subdir, dirs, files in os.walk(ROOTDIR):
		for file in files:
			if file == 'nor_traces_maxmin.npy':
				temp = np.load(os.path.join(subdir, file))
				#print(temp.shape)
				temp = np.mean(temp, axis=0)	# Average eatch traces in file
				temp = np.reshape(temp, (1,400))
				#print(tempT.shape)
				avg = np.append(avg, temp, axis=0) 	# Append to end trace
				#print(avg.shape)
				#print(os.path.join(subdir, file))
	#print(avg)
	return np.mean(avg, axis=0)	# Average end trace

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

def makeTraces(corr, traceArray, trigger, offset = 3328):
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



def main():
	templ_length = TEMPLATE_LENGTH

	#avg = averageOfOne(normMaxMin(np.fromfile('../data/outfile', dtype='float32')[2000000:3000000]), 406650)
	#np.save('avg_of_one.npy', avg)

	#avg = combine()
	#np.save('avg_combined.npy', avg)

	#avg = np.load('./avg_combined.npy')
	avg = np.load('./avg_of_one.npy')


	#test_trace = np.load('./test_trace.npy')
	#test_trace = normMaxMin(np.fromfile('../data/outfile', dtype='float32')[2000000:3000000])
	test_trace = normMaxMin(np.fromfile('../data/outfile', dtype='float32'))

	print('Correlating...')
	corr = signal.correlate(test_trace, avg, mode='full', method='auto')
	corr = normMaxMin(corr[templ_length:len(test_trace)])
	print('Distributing to bins...')
	corrAmplitudes, quantities = binDistribution(corr, 100)
	plt.figure(0)
	plt.plot(corrAmplitudes, quantities)

	traces, indexes = makeTraces(corr, test_trace, getTriggerLevel(corrAmplitudes, quantities, 0.1))
	print("Number of traces found: " + str(len(traces)))
	i = 1
	"""
	while i < len(traces):
		plt.figure(i)
		plt.plot(range(traces.shape[1]), traces[i])
		i += 1
	"""


	#print(np.amax(corr))
	#print(np.argmax(corr))

	plt.figure(i)
	plt.plot(range(len(indexes)), indexes)
	i+=1
	indexDiffs = np.array([], dtype='int')
	lastIndex = 0
	for index in indexes:
		temp = np.array([index - lastIndex], dtype='int')
		indexDiffs = np.append(indexDiffs, [index-lastIndex], axis=0)
		lastIndex = index
	print('Distributing indexes to bins...')
	indexDiffBins, quantities = binDistribution(indexDiffs, 8700, 0, 8700)
	plt.figure(i)
	plt.plot(indexDiffBins, quantities)
	#plt.plot(range(0, len(test_trace)), test_trace, range(np.argmax(corr)-templ_length, np.argmax(corr)), avg, range(templ_length, len(test_trace)), corr)
	plt.show()
	#plt.plot(range(0, 400), avg)
	#plt.show()

if __name__ == "__main__":
	main()
