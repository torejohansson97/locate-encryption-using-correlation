import correlation_tools as tct
import matplotlib.pyplot as plt
import numpy as np


def main(randomSeed=0):
    """
    For creating template and saving to file for reusing.
    """
    numTraces = 1
    withZeros = False
    filepath = '../data/our-data/templates/'
    numStr = str(numTraces)
    if numTraces >= 1000:
        temp = numTraces/1000
        if temp.is_integer():
            temp = int(temp)
        numStr = str(temp) + 'k'
    elif numTraces == 1:
        randomSeed = 5674 # Between 0 and 100000
        numStr = '_'+str(randomSeed)
    filename = 'avg'+numStr
    startIndex = 200
    #startIndex = 502390
    templateLength = 400
    if templateLength == 400:
        round = 'last'
        if round == 'first':
            startIndex = startIndex+800
            filename += '_firstround'
        elif round == 'last':
            startIndex = startIndex+3720
            filename += '_lastround'
    #avg = getAverage(numTraces, np.fromfile('../data/our-data/data-for-templates/100k.npy', dtype='float32'), startIndex, templateLength)
    dataSet = np.memmap('../data/our-data/for_template/100k_d10_k50_1avg_1rep/traces.npy', dtype='float32', mode='r', shape=(100000,4500))
    avg = tct.normMaxMin(getAverage(numTraces, dataSet, startIndex, templateLength, randomSeed))

    if withZeros and templateLength == 4100:
        filename += '_zeros'
        tempzeros = np.zeros(avg.shape)
        avg[1100:3800]=tempzeros[1100:3800]

    filename += '.npy'
    plt.plot(avg)
    plt.show()
    if input('Do you want to save to file ['+filename+']? (y/n)')[0] == 'y':
        saveToFile(filepath+filename, avg)
	#np.save('../data/our-data/templates/avg'+str(numTraces), avg)

def getAverage(numTraces, dataSet, startIndex, templateLength, randIndex=0):
    dataSet = dataSet[:, startIndex:startIndex+templateLength]
    if numTraces != len(dataSet):
        indexDiff = len(dataSet)//numTraces
        traces = np.empty((0,templateLength))
        for i in range(numTraces):
            #print('Adding trace #'+str(i*indexDiff))
            temp = dataSet[i*indexDiff+randIndex]
            temp = np.reshape(temp, (1,templateLength))
            traces = np.append(traces, temp, axis=0)
        dataSet = traces
    return np.mean(dataSet, axis=0)

def saveToFile(filepath, template):
    np.save(filepath, template)

if __name__ == '__main__':
    main()
