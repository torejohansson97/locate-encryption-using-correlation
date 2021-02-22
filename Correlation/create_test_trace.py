import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read

def soundNoise(filename):
	sound = read(filename)
	array = np.array(sound[1],dtype=float)
	return array

def whiteNoise(length, mean = 0, std = 1):
	return np.random.normal(mean, std, size=length)

def insertTrace(trace, testTrace, offset):
	for i in range(len(trace)):
		testTrace[i+offset] = trace[i]+testTrace[i+offset]
	return testTrace

def addSamples(trace1, trace2):
	for i in range(len(trace1)):
		trace2[i] += trace1[i]
	return trace2

def main():
	sNoise = soundNoise('../data/baloobas.wav')
	wNoise = whiteNoise(len(sNoise))
	testTrace = addSamples(wNoise, sNoise)
	trace = np.load('../data/ff-em-sca-data/for_testing/3m/10k_d6/1avg/nor_traces_maxmin.npy')[0]
	max = np.max(testTrace)
	min = np.min(testTrace)
	testTrace_scaled = np.array([(x - min) / (max - min) for x in testTrace])
	final = insertTrace(trace, testTrace_scaled, 100000)
	max = np.max(final)
	min = np.min(final)
	finalmaxmin = np.array([(x - min) / (max - min) for x in final])
	np.save('test_trace.npy', finalmaxmin)
	plt.plot(finalmaxmin[100000:100500])
	plt.show()



if __name__ == "__main__":
	main()
