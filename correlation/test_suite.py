import correlation_tools as tct
import matplotlib.pyplot as plt
import numpy as np
import os

def filterTest():
    createTemplateFile()
    template, test_trace = loadData()

    foundTraces = []
    avg_traces = np.empty((len(test_trace),400))
    arrayCut = 200000

    for i in range(len(test_trace)):
        traceArray = test_trace[i,arrayCut:]
        #traces = tct.getTracesFromArray(traceArray, template)
        traces = tct.getEncryptionBlockFromArray(traceArray, template)
        foundTraces.append(len(traces))
        #avg_traces[i] = tct.normMaxMin(tct.average(traces))
    print('Hittade traces: ' + str(foundTraces))

    plt.figure(10)
    plt.plot(traces[0])
    #plt.plot(avg_traces[9])

    tct.plotEnvelopeWithTrigger(test_trace[0], template)

def templateTest():
    arrayCut = 2500
    template, templateName = chooseTemplate('../data/our-data/templates')
    test_set = np.load('../data/test2/k2/traces.npy')[:,arrayCut:]
    tracesPerLine = 100
    totalTraces = tracesPerLine*len(test_set)
    plt.plot(test_set[0])
    plt.show()
    arrayCut = intInput('Enter number of samples to cut in beginning: ',0, test_set.shape[1]-(len(template)*2))
    tct.plotEnvelopeWithTrigger(test_set[2, arrayCut:], template)
    trigMultiplier = intInput('Enter value for trigger multiplier: ')

    peakVariance = 0
    foundTraces = []

    for i in range(len(test_set)):
        traceArray = test_set[i,arrayCut:]

        corr = tct.getCorrelation(traceArray, template, False)
        corrEnvelopeList = tct.getCorrEnvelopeList(corr)
        indices = tct.getTraceIndicesFromEnvelope(corr, corrEnvelopeList, 800, trigMultiplier)
        foundTraces.append(len(indices))
        #avg_traces[i] = tct.normMaxMin(tct.average(traces))
    print('Hittade traces: ' + str(foundTraces))
    writeToStatsFile('../data/our-data/templates/stats.txt', generateLineFromStats(templateName, sum(foundTraces), totalTraces, std, trigMult, avgPeakVal, peakVariance))

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

def chooseTemplate(templatesPath):
    templates = []
    i = 0
    for subdir, dirs, files in os.walk(templatesPath):
        for file in files:
            if file.endswith('.npy'):
                filepath = os.path.join(subdir, file)
                templates.append([subdir, file])
                i+=1
                print('['+str(i)+'] '+ file)
    choice = intInput('Which template do you want to use? (1-'+str(i)+')', 1, i)
    filepath = os.path.join(templates[choice-1][0], templates[choice-1][1])
    name = templates[choice-1][1]
    return np.load(filepath), name

def intInput(question, min=1, max=100):
    while True:
        try:
            strInput = input(question)
            value = int(strInput)
            if value in range(min,max+1):
                break
        except:
            pass
        print('Invalid input!')
    return value

def writeToStatsFile(filepath, line):
    while True:
        try:
            with open('filepath', 'a') as f:
                f.write(line)
                break
        except IOError:
            createStatsFile(filepath)
        if input('File did not exist, do you want to go again? [y/n]')[0] != 'y':
            break

def createStatsFile(filepath):
    line1 = '   Template file   |  Found   | Accur. | Total  | Standard | Trig. | Avg. peak |   Peak   |'
    line2 = '        name       |  traces  |  (%)   | traces |  dev.    | mult. |   value   | variance |'
    line3 = '‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾'
    f = open(filepath, 'w')
    for line in [line1, line2, line3]:
        f.write(line)
    file.close()

def generateLineFromStats(templateName, foundTraces, totalTraces, std, trigMult, avgPeakVal, peakVariance):
    """ Format with number of symbols per segment
    line1 = '   Template file   |  Found   | Accur. | Total  | Standard | Trig. | Avg. peak |   Peak   |'
    line2 = '        name       |  traces  |  (%)   | traces |  dev.    | mult. |   value   | variance |'
    line3 = '‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾'
    line4 = '          19             10        8        8       10         7         11         10    |'
    """
    percentage = round((float(foundTraces)/totalTraces)*100,2)
    if totalTraces > 1000:
        totalTraces = str(totalTraces/1000) + 'K'
    line = (centerInString(templateName, 19) + ' ' +
            centerInString(str(foundTraces), 10) + ' ' +
            centerInString(str(percentage), 8) + ' ' +
            centerInString(str(totalTraces), 8) + ' ' +
            centerInString(str(round(std,3)), 10) + ' ' +
            centerInString(str(trigMult), 7) + ' ' +
            centerInString(str(round(avgPeakVal,3)), 11) + ' ' +
            centerInString(str(round(peakVariance,3)), 10) + '|')
    return line

def centerInString(text, strLength):
    if len(text)>strLength:
        return text[0:strLength]
    elif len(text)<strLength:
        temp = ' '*strLength
        startIndex = (strLength-len(text))//2
        temp[startIndex:startIndex+len(text)] = text
        return temp
    return text

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
    userInput = input('Vilket test vill du göra, template (t) eller filter (f)?')[0]
    if userInput == 'f':
        filterTest()
    elif userInput == 't':
        templateTest()
