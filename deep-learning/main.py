import tensorflow as tf
import numpy as np 
import os, sys
from matplotlib import pyplot as plt

sys.path.append('../correlation')
import correlation_tools as ct


DIR = '../data/our-data/for_training'
#DIR = '../data/ff-em-sca-data/for_training/cable/100k_d1/100avg'

byteOfInterest = 15

def main():
	while True:
		inpt = input('1. Load data\n2. Generate model\n3. Train model\n4. Test model\n5. Evaluate model\n9. Exit\n')
		if inpt == '1':
			folder = input("Where is the data located?")
			traces, labels = load_data(DIR)
			plt.plot(traces[12393])
			plt.show()
		elif inpt == '2':
			model = create_attack_model()
		elif inpt == '3':
			try:
				history_log = train_model(traces, tf.keras.utils.to_categorical(labels, num_classes=256), model, 300, 128, './models/byte' + str(byteOfInterest) + '/attack_model_byte' + str(byteOfInterest) + '-{epoch:01d}.h5')
				#history_log = train_model(traces[:, 1139:1249], tf.keras.utils.to_categorical(labels, num_classes=256), model, 100, 128, './attack_model.h5')
				#history_log = train_model(traces[:, 130:240], tf.keras.utils.to_categorical(labels, num_classes=256), model, 100, 128, './models/byte' + str(byteOfInterest) + '/attack_model_byte' + str(byteOfInterest) + '-{epoch:01d}.h5')
				# TODO: Plot history
				print(history_log.history['val_accuracy'])
				print(history_log.history['accuracy'])
			except UnboundLocalError:
				print("Generate model first.")
			
		elif inpt == '4':
			test_model(traces, key, pt, './models/byte' + str(byteOfInterest) + '/attack_model_byte' + str(byteOfInterest) + '-40.h5')
		elif inpt == '5':
			modelNr = input("Which epoc do you want to evaluate?")
			evaluate_model(traces, tf.keras.utils.to_categorical(labels, num_classes=256), 128, './models/byte' + str(byteOfInterest) + '/attack_model_byte' + str(byteOfInterest) + '-' + str(modelNr) + '.h5')

		elif inpt == '9':
			exit()


def train_model(input, labels, model, epochs, batch_size, file_name):
	if  os.path.exists(file_name):
		if input('File already exists! Do you want to continue? y/n') == 'n':
			exit()
	
	save_model = tf.keras.callbacks.ModelCheckpoint(file_name)
	callbacks = [save_model]
	input_layer_shape = model.get_layer(index=0).input_shape
	
	if input_layer_shape[1] != len(input[0]): # Sanity check
		print("Error: model input shape %d instead of %d is not expected ..." % (input_layer_shape[1], len(input[0])))
		exit()

	if len(input_layer_shape) == 2: # MLP model
		reshaped_input = input

	elif len(input_layer_shape) == 3: # CNN model, expand dimentions
		reshaped_input = input.reshape((input.shape[0], input.shape[1], 1))

	else:
		print("Error: model input shape length %d is not expected ..." % len(input_layer_shape))
		exit()

	history = model.fit(x=reshaped_input, y=labels, batch_size=batch_size, verbose=1, epochs=epochs, callbacks=callbacks, validation_split=0.1)

	return history

def test_model(input, key, pt, model_file): #TODO:
	keyOfInterest = key[byteOfInterest]
	ptOfInterest = pt[:, byteOfInterest]
	try:
		model = load_model(model_file)
	except:
		print("Error: can't load Keras model file '%s'" % model_file)
		exit()

	# Get the input layer shape
	input_layer_shape = model.get_layer(index=0).input_shape

	# Sanity check
	if input_layer_shape[1] != len(input[0]):
		print("Error: model input shape %d instead of %d is not expected ..." % (
			input_layer_shape[1], len(input[0])))
		exit()

	# Adapt the data shape according our model input
	if len(input_layer_shape) == 2:
		# This is a MLP
		input_data = input
	elif len(input_layer_shape) == 3:
		# This is a CNN: reshape the data
		input_data = input
		input_data = input_data.reshape((input_data.shape[0], input_data.shape[1], 1))
	else:
		print("Error: model input shape length %d is not expected ..." % len(input_layer_shape))
		exit()

	# Predict our probabilities
	predictions = model.predict(input_data)

def evaluate_model(input, labels, batch_size, model_file):
	try:
		model = tf.keras.models.load_model(model_file)
	except:
		print("Error: can't load Keras model file '%s'" % model_file)
		exit()

	input_layer_shape = model.get_layer(index=0).input_shape
	
	if input_layer_shape[1] != len(input[0]): # Sanity check
		print("Error: model input shape %d instead of %d is not expected ..." % (input_layer_shape[1], len(input[0])))
		exit()

	if len(input_layer_shape) == 2: # MLP model
		reshaped_input = input

	elif len(input_layer_shape) == 3: # CNN model, expand dimentions
		reshaped_input = input.reshape((input.shape[0], input.shape[1], 1))

	else:
		print("Error: model input shape length %d is not expected ..." % len(input_layer_shape))
		exit()
	# Evaluate the model on the test data using `evaluate`
	print("Evaluate on test data")
	results = model.evaluate(reshaped_input, labels, batch_size=batch_size)
	print("test loss, test acc:", results)


def create_identification_model():
	model = tf.keras.models.Sequential()

	model.add(tf.keras.layers.Dense(100, input_dim=800, activation='relu'))  #input_dim=5  all are 100 nodes before

	for i in range(2):
		model.add(tf.keras.layers.Dense(100, activation='relu'))
	
	model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

	optimizer = tf.keras.optimizers.Adam(learning_rate=0.0001)   

	model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

	return model

def create_attack_model(classes=256):
	'''
	Model from Huanyu
	'''
	# 70-100 epoch ,128 batch_size, 110 points, 1139->1249
	model = tf.keras.models.Sequential()
	model.add(tf.keras.layers.Conv1D(input_shape=(110, 1) , filters=4, kernel_size=3, activation='relu', padding='same'))	
	model.add(tf.keras.layers.AveragePooling1D(pool_size=2,strides=1))   	
	
	model.add(tf.keras.layers.Conv1D( filters=8, kernel_size=3, activation='relu', padding='same'))	
	model.add(tf.keras.layers.AveragePooling1D(pool_size=2,strides=1)) 

	model.add(tf.keras.layers.Conv1D( filters=16, kernel_size=3, activation='relu', padding='same'))	
	model.add(tf.keras.layers.AveragePooling1D(pool_size=2,strides=1)) 	

	model.add(tf.keras.layers.Conv1D( filters=32, kernel_size=3, activation='relu', padding='same'))	
	model.add(tf.keras.layers.AveragePooling1D(pool_size=2,strides=1)) 
	
	model.add(tf.keras.layers.Flatten())
	
	#model.add(Dropout(0.2))
	
	model.add(tf.keras.layers.Dense(units = 200, activation = 'relu'))
	model.add(tf.keras.layers.Dense(units = 200, activation = 'relu'))
	
	model.add(tf.keras.layers.Dense(units = classes, activation = 'softmax',name='predictions'))	
	optimizer = tf.keras.optimizers.RMSprop(lr=0.0001) #0.0001
	
	model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])	
	
	return model

def load_data(folder, norm=True):
	if norm:
		j=0
		traces = np.empty((300000, 110))
		labels = np.empty(300000)
		for i in range(1,4):
			raw = np.memmap(folder + '/100k_d10_k' + str(i) + '_100avg/traces.npy', dtype='float32', mode='r', shape=(100000,4500))[:100000, 1137:1247]
			for trace in range(len(raw)):
				traces[j] = ct.normMaxMin(raw[trace])
				j+=1
			labels[i*100000-100000:i*100000] =  np.load(folder + '/100k_d10_k' + str(i) + '_100avg/s1_label.npy')[:,byteOfInterest]
			print(traces.shape)
			print(labels.shape)
	else:
		traces = np.memmap(folder + '/traces.npy', dtype='float32', mode='r', shape=(100000,4500))[:100000, 1137:1247]
		traces = traces.reshape(110, len(traces)) # Transpose
	
	
	#labels = labels.astype('int32')
	#traces = np.load(DIR + '/nor_traces_maxmin.npy')[:, 130:240]
	#labels = np.load(DIR + '/label_0.npy')
	

	return traces, labels

if __name__ == "__main__":
   main()
