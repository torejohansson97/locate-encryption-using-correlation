import correlation_tools as tct
import matplotlib.pyplot as plt
import numpy as np

def main():
    i=2
    templ_length = tct.TEMPLATE_LENGTH

    createTemplateFile()

    # För att plotta ett gammalt trace
    avg = np.load('../data/ff-em-sca-data/for_training/cable/100k_d1/100avg/nor_traces_maxmin.npy')
    plotGraph(avg[0], i)
    i+=1

    template, test_trace = loadData()

    plotGraph(template, i) # plotta templaten som används
    i+=1

    """
    Kod för att hitta traces ur array
    """
    foundTraces = []
    avg_traces = np.empty((len(test_trace),400), dtype='float32')
    for j in range(len(test_trace)):
    	traces, indexes = tct.getTracesFromArray(tct.normMaxMin(test_trace[j,200000:]), template, (j==7))
    	foundTraces.append(len(traces))
    	avg_traces[j] = tct.average(traces)
    print("Number of traces found: " + str(foundTraces))
    #plt.figure(i)
    #i+=1
    #plt.plot(range(traces.shape[1]), traces[10])
    plotGraph(range(avg_traces.shape[1]), avg_traces[0], i)
    i+=1

    """
    indexDiffBins, quantities = getIndexDiffBins(indexes)
    plt.figure(i)
    plt.plot(indexDiffBins, quantities)
    """
    #plt.plot(range(0, len(test_trace)), test_trace, range(np.argmax(corr)-templ_length, np.argmax(corr)), avg, range(templ_length, len(test_trace)), corr)
    plt.show()

def createTemplateFile():
    """
    For creating template and saving to file for reusing.
    """
    #avg = averageOfOne(normMaxMin(np.fromfile('../data/outfile', dtype='float32')[2000000:3000000]), 406650)
	#np.save('avg_of_one.npy', avg)

	#avg = np.load('./avg_of_one.npy')
	#tempzeros = np.zeros(avg.shape)
	#avg[1100:3800]=tempzeros[1100:3800]
	#np.save('avg_of_one_withzeros.npy', avg)

	#avg = combine()
	#np.save('avg_combined.npy', avg)

def loadData():
    """
    Loading template and trace array from files
    """
    #template = np.load('./avg_combined.npy')
    #template = np.load('./avg_of_one.npy')
    template = np.load('./avg_of_one_withzeros.npy')

    #traceArray = np.load('./test_trace.npy')
    #traceArray = normMaxMin(np.fromfile('../data/outfile', dtype='float32')[2000000:3000000])
    #traceArray = normMaxMin(np.fromfile('../data/outfile', dtype='float32'))
    traceArray = np.load('../data/test2/k2/traces.npy')
    return template, traceArray

def plotGraph(xAxis, yAxis, windowNr=None):
    """
    For plotting graphs more neatly
    """
    if windowNr == None:
        plt.figure(yAxis)
        plt.plot(xAxis)
    else:
        plt.figure(windowNr)
        plt.plot(xAxis, yAxis)

def getIndexDiffBins(indexes):
    """
    Code for putting index difference between found traces into bins for plotting
    """
    indexDiffs = np.array([], dtype='int')
    lastIndex = 0
    for index in indexes:
    	temp = np.array([index - lastIndex], dtype='int')
    	indexDiffs = np.append(indexDiffs, [index-lastIndex], axis=0)
    	lastIndex = index
    print('Distributing indexes to bins...')
    return tct.binDistribution(indexDiffs, 8700, 0, 8700)

def combine():
	avg = np.empty((0,400), float) #creating empty array
	print('Loading files...')
	for subdir, dirs, files in os.walk('../data/ff-em-sca-data'):
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

if __name__ == "__main__":
	main()
