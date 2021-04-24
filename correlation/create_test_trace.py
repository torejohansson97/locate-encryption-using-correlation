import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
import correlation_tools as ct

def soundNoise(filename):
	sound = read(filename)
	array = np.array(sound[1],dtype=float)
	return normMaxMin(array)

def whiteNoise(length, mean = 0, std = 1):
	return np.random.normal(mean, std, size=length)

def insertTrace(trace, bigTrace, offset):
	for i in range(len(trace)):
		bigTrace[i+offset] = trace[i]+bigTrace[i+offset]
	return bigTrace

def insertTraceAverage(trace, testTrace, offset):
	for i in range(len(trace)):
		testTrace[i+offset] = (trace[i]+testTrace[i+offset])/2
	return testTrace

def main():
	#sNoise = soundNoise('../data/baloobas.wav')
	traceName = 'traces_cable'
	traceShape = (1,1261568*50)
	originalTrace = np.memmap('../data/our-data/for_testing/long_traces/with_setup/'+traceName+'.npy', dtype='float32', mode='r', shape=traceShape)[:].copy()
	wNoise = whiteNoise(1261568*50, 0, np.std(originalTrace))
	testTrace = np.add(originalTrace, wNoise)
	#testTrace_scaled = normMaxMin(testTrace)

	#trace = np.load('../data/ff-em-sca-data/for_testing/3m/10k_d6/1avg/nor_traces_maxmin.npy')[0]
	#trace2 = np.load('../data/ff-em-sca-data/for_testing/3m/10k_d6/1avg/nor_traces_maxmin.npy')[100]

	#final = insertTrace(trace, testTrace, 100000)
	#final = insertTrace(trace2, final, 350000)

	#testTrace = ct.normMaxMin(testTrace)
	output = np.memmap('../data/our-data/for_testing/long_traces/with_setup/'+traceName+'_noisy.npy', dtype='float32', mode='w+', shape=traceShape)
	output[0] = testTrace
	#np.save('test_trace.npy', finalmaxmin)
	plt.plot(output[0])
	output.flush()
	plt.show()



if __name__ == "__main__":
	main()
