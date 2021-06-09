# Simon Weideskog and Tore Johansson
# Last edited: 2021-06-09
"""
Script for testing templates performance compared to each together
in different scenarios.
"""

import correlation_tools as tct
import matplotlib.pyplot as plt
import numpy as np
import os

def attackTest():
    """
    Function for testing attack on noisy traces.
    """
    traceName = 'traces_antenna'
    addNoise = False
    normalizeEnvelope = True

    template, templateName = chooseTemplate('../data/our-data/templates')
    traces = np.memmap(f'../data/our-data/for_testing/long_traces/with_setup/{traceName}.npy', dtype='float32', mode='r', shape=(50,1261568))
    rows = len(traces)
    tracesPerRow = 50
    totalTraces = tracesPerRow*rows
    traceArray = traces[3,:]
    plt.rcParams["figure.figsize"] = (8,3)
    plt.gcf().subplots_adjust(bottom=0.15)
    plt.plot(traceArray)
    plt.xlabel('Sample number')
    plt.ylabel('Amplitude')
    plt.show()
    #stdNoise = np.std(traceArray)
    stdNoise = 0.003
    print('stdNoise = '+ str(stdNoise))
    if addNoise:
        #plt.plot(traceArray+0.025)
        traceArray = np.add(traceArray, whiteNoise(1261568, 0, stdNoise))
        #plt.plot(traceArray)
        #plt.show()
    tct.plotEnvelopeWithTrigger(traceArray, template, normalizeEnvelope)
    trigMultiplier = intInput('Enter value for trigger multiplier: ')

    foundTraces = []
    blocks = np.empty((0,4100))
    for i in range(rows):
        print('Current trace: '+str(i*tracesPerRow)+'/'+str(totalTraces), end='\r')
        traceArray = traces[i,:]
        if addNoise:
            traceArray = np.add(traceArray, whiteNoise(1261568, 0, stdNoise))

        encryptionBlocks = tct.getEncryptionBlocksFromArray(traceArray, template, 0, trigMultiplier, normalizeEnvelope)
        foundTraces.append(len(encryptionBlocks))
        blocks = np.append(blocks, encryptionBlocks, axis=0)
    print('\a')
    print('Hittade traces: ' + str(sum(foundTraces))+'/'+str(totalTraces))
    plt.plot(np.mean(blocks, axis=0))
    plt.show()


def templateTest():
    """
    Function for testing performance of different templates.
    """
    normalizeEnvelope = False
    addNoise = True
    template, templateName = chooseTemplate('../data/our-data/templates')
    templateName = templateName.strip('.npy')
    test_set = np.memmap(f'../data/our-data/for_testing/10k_d10_k{1}_1avg_10rep/traces.npy', dtype='float32', mode='r', shape=(10000,130000))
    tracesPerRow = 10
    rowsPerKey = 5 #len(test_set)
    keyFolders = 2 #/5
    totalTraces = tracesPerRow*rowsPerKey*keyFolders
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
            numIndices, peakMean, peakVariance, meanCorr, std = tct.getBlockStatsFromEnvelope(corr, corrEnvelopeList, 800, trigMultiplier)
            foundTraces.append(numIndices)
            #if numIndices > 10: # Useful for finding errors in data set
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
    """
    Letting the user choose which template to use from the specified directory.
    """
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
    """
    Only accepts correct integer input to avoid crashing.
    """
    while True:
        try:
            strInput = input(question)
            value = int(strInput)
            if value >= min and value <= max:
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
    if userInput == 't':
        templateTest()
    elif userInput == 'a':
        attackTest()
