import correlation_tools as tct
import matplotlib.pyplot as plt
import numpy as np


def main():
    """
    For creating template and saving to file for reusing.
    """
    numTraces = 1
    withZeros = True
    filepath = '../data/our-data/templates/'
    filename = 'avg'+str(numTraces)
    #startIndex = 200
    startIndex = 502390
    templateLength = 400
    if templateLength == 400:
        round = 'first'
        if round == 'first':
            startIndex = startIndex+800
            filename += '_firstround'
        elif round == 'last':
            startIndex = startIndex+3700
            filename += '_lastround'
    #avg = getAverage(numTraces, np.fromfile('../data/our-data/data-for-templates/100k.npy', dtype='float32'), startIndex, templateLength)
    avg = tct.normMaxMin(getAverage(numTraces, np.load('../data/test2/k1/traces.npy'), startIndex, templateLength))

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

def getAverage(numTraces, dataSet, startIndex, templateLength):
    indexDiff = len(dataSet)//numTraces

    traces = np.empty((0,templateLength))
    for i in range(numTraces):
        print('Adding trace #'+str(i*indexDiff))
        temp = dataSet[i*indexDiff, startIndex:startIndex+templateLength]
        temp = np.reshape(temp, (1,templateLength))
        traces = np.append(traces, temp, axis=0)
    return np.mean(traces, axis=0)

def saveToFile(filepath, template):
    np.save(filepath, template)

if __name__ == '__main__':
    main()
