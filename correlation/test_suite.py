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

def attackTest():
    template, templateName = chooseTemplate('../data/our-data/templates')
    traces = np.memmap('../data/our-data/for_testing/long_traces/with_setup/traces_antenna.npy', dtype='float32', mode='r', shape=(50,1261568))
    rows = len(traces)
    tracesPerRow = 50
    totalTraces = tracesPerRow*rows
    #plt.plot(test_set[0])
    #plt.show()
    #arrayCut = 400000
    tct.plotEnvelopeWithTrigger(traces[3,:], template)
    #trigMultiplier = 10
    trigMultiplier = intInput('Enter value for trigger multiplier: ')

    foundTraces = []
    blocks = np.empty((0,4100))
    for i in range(rows):
        print('Current trace: '+str(i*tracesPerRow)+'/'+str(totalTraces), end='\r')
        traceArray = traces[i,:]

        encryptionBlocks = tct.getEncryptionBlocksFromArray(traceArray, template, 0, trigMultiplier, True)
        print(len(encryptionBlocks))
        foundTraces.append(len(encryptionBlocks))
        blocks = np.append(blocks, encryptionBlocks, axis=0)
    print('\a')
    print('Hittade traces: ' + str(sum(foundTraces))+'/'+str(totalTraces))
    plt.plot(np.mean(blocks, axis=0))
    plt.show()


def templateTest():
    normalizeEnvelope = False
    addNoise = True
    #arrayCut = 2500
    template, templateName = chooseTemplate('../data/our-data/templates')
    templateName = templateName.strip('.npy')
    #test_set = np.load('../data/test2/k2/traces.npy')[:,arrayCut:]
    test_set = np.memmap(f'../data/our-data/for_testing/10k_d10_k{1}_1avg_10rep/traces.npy', dtype='float32', mode='r', shape=(10000,130000))
    tracesPerRow = 10
    rowsPerKey = len(test_set)
    keyFolders = 5 #/5
    totalTraces = tracesPerRow*rowsPerKey*keyFolders
    #plt.plot(test_set[0])
    #plt.show()
    arrayCut = 0
    #arrayCut = intInput('Enter number of samples to cut in beginning: ',0, test_set.shape[1]-(len(template)*2))
    traceArray = test_set[0,arrayCut:]
    stdNoise = 0.003
    print('stdNoise = '+ str(stdNoise))
    if addNoise:
        #plt.plot(traceArray+0.025)
        templateName+='_n'
        traceArray = np.add(traceArray, whiteNoise(130000, 0, stdNoise))
        #plt.plot(traceArray)
        #plt.show()
    tct.plotEnvelopeWithTrigger(traceArray, template, normalizeEnvelope)
    #trigMultiplier = 6
    trigMultiplier = intInput('Enter value for trigger multiplier: ',1,10000000)

    foundTraces = []
    peakMeanList = []
    peakVarList = []
    meanCorrList = []
    stdList = []

    for key in range(1,keyFolders+1):
        test_set = np.memmap(f'../data/our-data/for_testing/10k_d10_k{key}_1avg_10rep/traces.npy', dtype='float32', mode='r', shape=(10000,130000))
        for i in range(rowsPerKey):
            print('Current trace: '+str((i*tracesPerRow)+(key-1)*rowsPerKey*tracesPerRow)+'/'+str(totalTraces), end='\r')
            traceArray = test_set[i,arrayCut:]
            if addNoise:
                traceArray = np.add(traceArray, whiteNoise(130000, 0, stdNoise))

            corr = tct.getCorrelation(traceArray, template, True)
            corrEnvelopeList = tct.getCorrEnvelopeList(corr, normalizeEnvelope, traceArray)
            numIndices, peakMean, peakVariance, meanCorr, std = tct.getTraceStatsFromEnvelope(corr, corrEnvelopeList, 800, trigMultiplier)
            foundTraces.append(numIndices)
            #if numIndices > 10:
            #    tct.plotEnvelopeWithTrigger(traceArray, template)
            if peakMean != None:
                peakMeanList.append(peakMean)
                peakVarList.append(peakVariance)
            meanCorrList.append(meanCorr)
            stdList.append(std)
    print('\a')
    avgPeakVal = np.mean(peakMeanList)
    peakVariance = np.mean(peakVarList)
    meanCorr = np.mean(meanCorrList)
    std = np.mean(stdList)
    print('Hittade traces: ' + str(sum(foundTraces)))
    writeToStatsFile('../data/our-data/templates/stats.txt',
                     generateLineFromStats(templateName, sum(foundTraces),
                                           totalTraces, meanCorr, std, trigMultiplier,
                                           avgPeakVal, peakVariance))


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
    if not i:
        print('No template found, closing script...')
        exit()
    choice = intInput('Which template do you want to use? (1-'+str(i)+')', 1, i)
    filepath = os.path.join(templates[choice-1][0], templates[choice-1][1])
    name = templates[choice-1][1]
    return np.load(filepath), name

def intInput(question, min=1, max=100):
    while True:
        try:
            strInput = input(question)
            value = int(strInput)
            if value > min and value <= max:
                break
        except ValueError:
            exit()
        except:
            pass
        print('Invalid input!')
    return value

def writeToStatsFile(filepath, line):
    try:
        if os.stat(filepath).st_size == 0:
            createStatsFile(filepath)
    except FileNotFoundError:
        createStatsFile(filepath)
    try:
        with open(filepath, 'a', encoding = 'utf-8') as f:
            f.write(line)
    except IOError:
        print('Writing to file failed')

def createStatsFile(filepath):
    line1 = '   Template file   |  Found   | Accur. | Total  |  Mean  | Standard | Trig. | Avg. peak |   Peak   |\n'
    line2 = '        name       |  traces  |  (%)   | traces |  corr. |  dev.    | mult. |   value   | variance |\n'
    line3 = '‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n'
    with open(filepath, 'w', encoding = 'utf-8') as f:
        for line in [line1, line2, line3]:
            f.write(line)


def generateLineFromStats(templateName, foundTraces, totalTraces, meanCorr, std, trigMult, avgPeakVal, peakVariance):
    """ Format with number of symbols per segment
    line1 = '   Template file   |  Found   | Accur. | Total  |  Mean  | Standard | Trig. | Avg. peak |   Peak   |'
    line2 = '        name       |  traces  |  (%)   | traces |  corr. |  dev.    | mult. |   value   | variance |'
    line3 = '‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾'
    line4 = '         19        |     10        8        8       8        10         7         11         10    |'
    """
    percentage = round((float(foundTraces)/totalTraces)*100,4)
    if totalTraces >= 1000:
        temp = totalTraces/1000
        if temp.is_integer():
            temp = int(temp)
        totalTraces = str(temp) + 'K'
    line = (centerInString(templateName, 19) + ';' +
            centerInString(str(foundTraces), 10) + ';' +
            centerInString(str(percentage), 8) + ';' +
            centerInString(str(totalTraces), 8) + ';' +
            centerInString(str(round(meanCorr,4)), 8) + ';' +
            centerInString(str(round(std,4)), 10) + ';' +
            centerInString(str(trigMult), 7) + ';' +
            centerInString(str(round(avgPeakVal,4)), 11) + ';' +
            centerInString(str(round(peakVariance,5)), 10) + '\n')
    return line

def centerInString(text, strLength):
    if len(text)>strLength:
        return text[0:strLength]
    elif len(text)<strLength:
        startIndex = (strLength-len(text))//2
        temp = (' '*startIndex) + text
        return temp + (' '*(strLength-len(temp)))
    return text

def whiteNoise(length, mean = 0, std = 1):
	return np.random.normal(mean, std, size=length)

if __name__ == "__main__":
    userInput = input('Vilket test vill du göra, template (t), filter (f) eller attack (a)?')[0]
    if userInput == 'f':
        filterTest()
    elif userInput == 't':
        templateTest()
    elif userInput == 'a':
        attackTest()
