import correlation_tools as tct
import matplotlib.pyplot as plt
import numpy as np
from test_suite import *
plt.rcParams["figure.figsize"] = (8,3)
plt.gcf().subplots_adjust(left=0.08, right=0.98, bottom=0.15)


trace = np.memmap('../data/our-data/for_testing/long_traces/with_setup/traces_cable.npy', dtype='float32', mode='r', shape=(50,1261568))
#trace = np.memmap('../data/our-data/for_testing/long_traces/with_setup/traces_antenna.npy', dtype='float32', mode='r', shape=(1,1261568*50))
template = np.load('../data/our-data/templates/avg100_firstround.npy')

#tct.plotEnvelopeWithTrigger(trace[0,:], template)
#corr = tct.getCorrelation(trace[0,:], template)
plt.figure(1)
plt.plot(template)
plt.xlabel('Sample number')
plt.ylabel('Amplitude')
plt.show()
