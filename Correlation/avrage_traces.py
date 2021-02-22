import numpy as np
import matplotlib.pyplot as plt

def combine():
	traces = np.load('./ff-em-sca-data/for_training/cable/100k_d1/100avg/nor_traces_maxmin.npy')
	for i in range(2,6):
		traces = np.append(traces, np.load('./ff-em-sca-data/for_training/cable/100k_d'+str(i)+'/100avg/nor_traces_maxmin.npy'), axis = 0)
	avg0 = np.average(traces, axis=0)
	del(traces)

def main():
	import os
	rootdir = '../ff-em-sca-data'
	avg = np.empty((0,400), float) #creating empty array

	for subdir, dirs, files in os.walk(rootdir):
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
	avg = np.mean(avg, axis=0)	# Average end trace
	print(avg.shape)
	plt.plot(range(0, 400), avg)
	plt.show()

if __name__ == "__main__":
	main()
