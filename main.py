#!/usr/bin/python3

import sys, getopt
from datetime import datetime
import numpy as np
import tensorflow as tf

def loadData(dataPath, traceFile, labelFile):
	traces = np.load(dataPath + traceFile)
	labels = np.load(dataPath + labelFile)
	return traces, labels

def setupModel(classes=256):
	model = tf.keras.Sequential()

	model.add(tf.keras.layers.Dense(100, input_dim=5, activation='relu')) # Input layer:


	for i in range(5):
		model.add(tf.keras.layers.Dense(100, activation='relu')) # Hidden layers:

	model.add(tf.keras.layers.Dense(classes, activation='softmax')) # Output layer:

	optimizer = tf.keras.optimizers.Adam(learning_rate=0.0001)

	model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

	return model

def trainModel(inputData, labels, model, save_model_path, save_model_name,batch_size, epochs):
	# Save model every epoch
	saveModel = tf.keras.callbacks.ModelCheckpoint(save_model_path + save_model_name)
	callbacks = [saveModel]
	# Get the input layer shape
	input_layer_shape = model.get_layer(index=0).input_shape
    # Sanity check
	if input_layer_shape[1] != len(inputData[0]):
		print("Error: model input shape %d instead of %d is not expected ..." % (input_layer_shape[1], len(inputData[0])))
		sys.exit(-1)
	
	if len(input_layer_shape) == 2:
		print('Ok!')
	else:
		print('Error: model imput shape length %d is not expected...' % len(input_layer_shape))
		sys.exit(-1)

	
	history = model.fit(x=inputData, y=tf.keras.utils.to_categorical(labels, num_classes=256), batch_size=batch_size, verbose=1, epochs=epochs, callbacks=callbacks, validation_split=0.1)

	return history

def main(argv):
	dataPath = ''
	try:
		opts, args = getopt.getopt(argv,"hi:",["ifile="])
	except getopt.GetoptError:
		print('test.py -i <dataPath>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('test.py -i <dataPath>')
			sys.exit()
		elif opt in ("-i", "--ifile"):
			dataPath = arg
	    
	NUMBER = 500000
	
	rawTraces, rawLabels = loadData(dataPath, 'nor_traces_maxmin.npy', 'label_0.npy') 

	rawTraces = rawTraces[:NUMBER]
	traces = rawTraces[:,[147,148,149,150,151]] 

	labels = rawLabels[:NUMBER]

	epochs = 100
	batch_size = 128
	model_folder = 'Models/'
	model_name = 'mlp_model_' + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + '.h5'

	model = setupModel()
	history_log = trainModel(traces, labels, model, model_folder,model_name, batch_size, epochs)

	#print(history_log.history['val_accuracy'])

	acc = np.array(history_log.history['val_accuracy'])
	loss = np.array(history_log.history['val_loss'])

	np.save(model_folder + 'Acc.npy', acc)
	np.save(model_folder + 'Loss.npy', loss)

if __name__ == "__main__":
	main(sys.argv[1:])

