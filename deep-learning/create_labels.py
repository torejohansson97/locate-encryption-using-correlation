from aes import *
import numpy as np
#DIR = '../data/our-data/for_training/100k_d10_k5_100avg'
DIR = '../data/ff-em-sca-data/for_training/cable/100k_d4/100avg'

def main():
	key = np.load(DIR + '/key.npy')
	pt = np.load(DIR + '/pt.npy')
	key = key.reshape(16)
	#print(key.type)
	sBox1out(key, pt)

def sBox1out(key, pt):
	s1out = []
	expKey = expandKey(key)
	
	for text in pt:
		xorText = add_sub_key(text, expKey)
	
		s1out.append(sBox(xorText))

	np.save(DIR + '/s1_label.npy', s1out)

def add_sub_key(text, key):
	xorText = []
	for byte in range(len(text)):
		xorText.append(text[byte] ^ key[byte])

	return xorText

def sBox(text):
	sOut = []
	for byte in text:
		x = byte >> 4
		y = byte & 15
		sOut.append(aes_sbox[x][y])
	
	return sOut

def expandKey(key):
	keyGrid = expand_key(key, 0)
	key = []
	for row in keyGrid:
		for byte in row:
			key.append(byte)
	
	return key

if __name__ == "__main__":
   main()
