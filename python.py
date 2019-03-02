import krpc
import serial
import time
import threading
import struct


running = True
server = None
arduino = None
arduinoport = 'COM5' #which COM port to listen and send data

while server is None or arduino is None:
	#We do not know if the server is online, so we want python to try to connect.
	try: 
		#The next line starts the connection with the server. It describes itself to the game as controller.
		server = krpc.connect(name ='Controller')
		#Now let's connect to the Arduino
		arduino = serial.Serial(port = arduinoport, baudrate = 115200)
	except ConnectionRefusedError: #error raised whe failing to connect to the server.
		print("Server offline")
		time.sleep(5) #sleep 5 seconds
		server = None
		arduino = None
	except serial.SerialException: #error raised when failling to connect to an arduino
		#TIPP: check if the Arduino serial monitor is off! or any other program using the arduino
		print("Arduino Connection Error.")	
		time.sleep(5)
		server = None
		arduino = None
		
time.sleep(2)
print("Started")
#The program has sucessfully started
while running:
	#PROBLEM: If the vessel is destroyed, or we switch to the hangar or anything, we can no longer controll it
	#  The Program will then fail.
	#SOLUTION: the "try:" statement
	#  If anything goes wrong inside a "try" block, 
	#  we can continue the program if we "catch" the error in the except clauses.	
	try:
		scene = server.krpc.current_game_scene
		if scene != server.krpc.current_game_scene.flight:
			time.sleep(1) #KSP is not in flight mode. Wait one second and check again.
			continue #skip the rest of the loop and check again.

		#We now tell the server what stuff we want streamed.
		print("Ready to go")
		vessel = server.space_center.active_vessel
		Arduinomessage = ArduinoSerial(arduino)

		#And at last we can start sending the data from the Arduino.
		while running:
			Cpacket = Arduinomessage.readMessage('<','>')

			vessel.control.yaw = remapByte(Cpacket[2],-1,1)
			vessel.control.pitch = remapByte(Cpacket[0],-1,1)
			vessel.control.roll = remapByte(Cpacket[1],-1,1)

			pass
		
	except krpc.error.RPCError as e:
		print("KSP Scene Changed!")
		time.sleep(1)
	except ConnectionAbortedError:
		print("KSP has Disconnected.")
		running = False #we can now end the program.


def remapByte(input, min, max):
	if input == "":  # need to check if input is empty, else code stop
		return 0
	else:
		input = int(input)
		range = max-min
		return input*range/1023 + min
    


#Read message by structsize
#Arduino Struct:
#  int Pitch;            //  0 ; 0 -> 1023
#  int Roll;             //  1 ; 0 -> 1023
#  int Yaw;              //  2 ; 0 -> 1023

class ArduinoSerial:
	def __init__(self, arduino):
		self.arduino = arduino

	def readMessage(self,startmarker, endMarker):
		# wait for data from arduino
		myByte = self.arduino.read(1).decode('utf-8')
		if myByte == startmarker:
			data = self.arduino.read(6)		#read byte length of the Cpacket struct
			myByte = self.arduino.read(1).decode('utf-8')
			if myByte == endMarker:
				# is  a valid message struct
				new_values = struct.unpack('<hhh', data) #unpack the struct
				return new_values    
