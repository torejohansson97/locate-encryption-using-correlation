import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read

def normMaxMin(inputArray):
	max = np.max(inputArray)
	min = np.min(inputArray)
	return np.array([(x - min) / (max - min) for x in inputArray])

def soundNoise(filename):
	sound = read(filename)
	array = np.array(sound[1],dtype=float)
	return normMaxMin(array)

def whiteNoise(length, mean = 0, std = 1):
	return np.random.normal(mean, std, size=length)

def insertTrace(trace, testTrace, offset):
	for i in range(len(trace)):
		testTrace[i+offset] = trace[i]+testTrace[i+offset]
	return testTrace

def insertTraceAverage(trace, testTrace, offset):
	for i in range(len(trace)):
		testTrace[i+offset] = (trace[i]+testTrace[i+offset])/2
	return testTrace

def addSamples(trace1, trace2):
	for i in range(len(trace1)):
		trace2[i] += trace1[i]
	return trace2

def main():
	sNoise = soundNoise('../data/baloobas.wav')
	wNoise = whiteNoise(len(sNoise))
	testTrace = addSamples(wNoise, sNoise)
	testTrace_scaled = normMaxMin(testTrace)

	trace = np.load('../data/ff-em-sca-data/for_testing/3m/10k_d6/1avg/nor_traces_maxmin.npy')[0]

	final = insertTrace(trace, testTrace, 100000)
	finalmaxmin = normMaxMin(final)
	np.save('test_trace.npy', finalmaxmin)
	plt.plot(finalmaxmin[99000:101000])
	plt.show()



if __name__ == "__main__":
	main()
