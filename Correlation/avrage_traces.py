import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import os

ROOTDIR = '../ff-em-sca-data'

def combine():
	avg = np.empty((0,400), float) #creating empty array
	plot('Loading files...')
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

def main():
	avg = combine()
	test_trace = np.load('./test_trace.npy')
	corr = signal.correlate(test_trace, avg, mode='full', method='auto')
	print(np.amax(corr))
	print(np.argmax(corr))

	#plt.plot(range(0, 400), avg)
	#plt.show()

if __name__ == "__main__":
	main()
