import correlation_tools as tct
import matplotlib.pyplot as plt
import numpy as np
from test_suite import *



trace = np.memmap('../data/our-data/for_testing/long_traces/with_setup/traces_antenna.npy', dtype='float32', mode='r', shape=(50,1261568))
#trace = np.memmap('../data/our-data/for_testing/long_traces/with_setup/traces_cable.npy', dtype='float32', mode='r', shape=(1,1261568*50))
template = np.load('../data/our-data/templates/avg100.npy')
#plt.plot(trace[0])
#plt.show()
tct.plotEnvelopeWithTrigger(trace[0,:], template)
