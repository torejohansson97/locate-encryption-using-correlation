import numpy as np
import matplotlib.pyplot as plt

avg = np.load('./ff-em-sca-data/for_training/cable/100k_d1/100avg/nor_traces_maxmin.npy')
avg = avg[0]
traces = np.load('./ff-em-sca-data/for_training/cable/100k_d1/100avg/nor_traces_maxmin.npy')
for i in range(2,6):
	traces = np.append(traces, np.load('./ff-em-sca-data/for_training/cable/100k_d'+str(i)+'/100avg/nor_traces_maxmin.npy'), axis = 0)
avg0 = np.average(traces, axis=0)
del(traces)

traces = np.load('./ff-em-sca-data/for_training/cable/20k_d1/100avg/nor_traces_maxmin.npy')
for i in range(2,6):
	traces = np.append(traces, np.load('./ff-em-sca-data/for_training/cable/20k_d'+str(i)+'/100avg/nor_traces_maxmin.npy'), axis = 0)
avg1 = np.average(traces, axis=0)
del(traces)

traces = np.load('./ff-em-sca-data/for_training/8m/20k_d1/100avg/nor_traces_maxmin.npy')
for i in range(1,6):
	traces = np.append(traces, np.load('./ff-em-sca-data/for_training/8m/20k_d'+str(i)+'/100avg/nor_traces_maxmin.npy'), axis = 0)
avg2 = np.average(traces, axis=0)
del(traces)

traces = np.load('./ff-em-sca-data/for_training/4m/20k_d1/100avg/nor_traces_maxmin.npy')
for i in range(1,6):
	traces = np.append(traces, np.load('./ff-em-sca-data/for_training/4m/20k_d'+str(i)+'/100avg/nor_traces_maxmin.npy'), axis = 0)
avg3 = np.average(traces, axis=0)
del(traces)

traces = np.load('./ff-em-sca-data/for_training/2m/20k_d1/100avg/nor_traces_maxmin.npy')
for i in range(1,6):
	traces = np.append(traces, np.load('./ff-em-sca-data/for_training/2m/20k_d'+str(i)+'/100avg/nor_traces_maxmin.npy'), axis = 0)
avg4 = np.average(traces, axis=0)
del(traces)

traces = np.load('./ff-em-sca-data/for_training/1m/20k_d1/100avg/nor_traces_maxmin.npy')
for i in range(1,6):
	traces = np.append(traces, np.load('./ff-em-sca-data/for_training/1m/20k_d'+str(i)+'/100avg/nor_traces_maxmin.npy'), axis = 0)
avg5 = np.average(traces, axis=0)
del(traces)

avg = np.append(avg, avg0, axis = 0)
avg = np.append(avg, avg1, axis = 0)
avg = np.append(avg, avg2, axis = 0)
avg = np.append(avg, avg3, axis = 0)
avg = np.append(avg, avg4, axis = 0)
avg = np.append(avg, avg5, axis = 0)
avg = np.average(avg, axis = 0)
plt.plot(range(0, 400), avg)
plt.show()
