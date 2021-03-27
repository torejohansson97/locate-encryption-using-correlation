import serial

class TargetDevice:
	def __init__(self, port):
		self.__device = serial.Serial(port, baudrate=115200, timeout=10)

	def enterTinyAES(self):
		self.__device.write(b'n') # Enter tinyAES
		self.__device.readline()

	def exitTinyAES(self):
		self.__device.write(b'q') # Quit tinyAES
		self.__device.readline()

	def setChannel(self, channel='0'):
		#print("Set channel")
		self.__device.write(b'a')
		print(self.__device.readline())
		self.__device.write(b'0\r\n')
		print(self.__device.readline())

	def setPower(self, power='0'):
		#print("Set pwr")
		self.__device.write(b'p0')
		print(self.__device.readline())
		print(self.__device.readline())

	def startCarrier(self):
		self.__device.write(b'c')

	def stopCarrier(self):
		self.__device.write(b'e')

	def setRepetition(self, repetiotion=2000):
		#print("Set rep")
		self.__device.write(b'n' + str(repetiotion).encode() + b'\r\n')
		self.__device.readline()  
		
	def setKey(self, key):
		# Assumes i tinyAES mode
		#print("Set key")
		command_line = '%s%s\r' % ('k', " ".join(str(char) for char in key))
		self.__device.write(command_line.encode())
		#print(self.__device.readline())
		self.__device.readline()

	def setPlainText(self, text):
		# Assumes i tinyAES mode
		#print("\nSet PT")
		command_line = '%s%s\r' % ('p', " ".join(str(char) for char in text))
		self.__device.write(command_line.encode())
		#print(command_line.encode())
		#print(self.__device.readline())
		self.__device.readline()
			
	def runEncryption(self):
		#print("Encrypting...")
		self.__device.write(b'r')
		#print(self.__device.read_until(b'Done\r\n'))
		self.__device.read_until(b'Done\r\n')

	def printMenu(self):
		self.__device.write(b'h')
		self.__device.read_until(b'q: Quit aes_masked mode\r\n') # Last menu string

	def close(self):
		self.__device.close()