# Simon Weideskog and Tore Johansson
# Last edited: 2021-05-26
"""
Script for creating templates.
"""

import correlation_tools as tct
import matplotlib.pyplot as plt
import numpy as np

"""
Following constants depends on encryption implementation
and need to be adjusted for different kinds of targets.
"""
BLOCK_LENGTH = 4100
ROUND_LENGTH = 400
FIRSTROUND_START = 800
LASTROUND_START = 3720

def main(randomSeed = 0):
    """
    Creating a template, then plotting it and
    asking if you want to save the template to file.
    """
    numTraces = 1 # Number of encryptions used for creating the template (with averaging)
    withZeros = False # 'True' replaces round 2-9 with zeros
    templateLength = 4100 # Length of temp., 4100=Encr. block, 400=Encr. round
    startIndex = 200 # Index in trace where encryption block starts
    round = 'last' # Choose between 'first' or 'last' round
    outputFilepath = '../data/our-data/templates/'

    numStr = str(numTraces)
    if numTraces >= 1000: # Automatically renames '10 000' to '10k'
        temp = numTraces/1000
        if temp.is_integer():
            temp = int(temp)
        numStr = str(temp) + 'k'
    elif numTraces == 1:
        randomSeed = 0 # Used to choose exactly which encryption block to use for Avg1
        numStr += '_'+str(randomSeed)
    filename = 'avg'+numStr

    if templateLength == ROUND_LENGTH:
        if round == 'first':
            startIndex = startIndex+FIRSTROUND_START
            filename += '_firstround'
        elif round == 'last':
            startIndex = startIndex+3720 # 3720 depends on encryption implementation and may vary
            filename += '_lastround'
    dataSet = np.memmap('../data/our-data/for_template/100k_d10_k50_1avg_1rep/traces.npy', dtype='float32', mode='r', shape=(100000,4500))
    avg = tct.normMaxMin(getAverage(numTraces, dataSet, startIndex, templateLength, randomSeed))

    if withZeros and templateLength == BLOCK_LENGTH:
        filename += '_zeros'
        tempzeros = np.zeros(avg.shape)
        avg[1100:3800]=tempzeros[1100:3800]

    filename += '.npy'
    plt.plot(avg)
    plt.show()
    if input('Do you want to save to file ['+filename+']? (y/n)')[0] == 'y':
        saveToFile(outputFilepath+filename, avg)

def getAverage(numTraces, dataSet, startIndex, templateLength, randIndex=0):
    """
    Returns average of {numTraces} encryptions from data set.
    Automatically uses encryptions distributed over the data set
    rather than just the first {numTraces} encryptions.
    """
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
    """
    Saving template to file.
    """
    np.save(filepath, template)

if __name__ == '__main__':
    main()
