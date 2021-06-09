import correlation_tools as tct
import matplotlib.pyplot as plt
import numpy as np
from test_suite import *
plt.rcParams["figure.figsize"] = (8,3)
plt.gcf().subplots_adjust(left=0.08, right=0.98, bottom=0.15)


trace = np.memmap('../data/our-data/for_template/100k_d10_k50_1avg_1rep/traces.npy', dtype='float32', mode='r', shape=(100000,4500))
template = np.load('../data/our-data/templates/avg100_firstround.npy')

plt.figure(1)
plt.plot(trace)
plt.xlabel('Sample number')
plt.ylabel('Amplitude')
plt.show()
