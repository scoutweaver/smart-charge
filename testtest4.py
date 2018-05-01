import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)  #set the pin numbering system
GPIO.setwarnings(False) #stop displaying the warnings

GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(10, GPIO.OUT)
GPIO.setup(9, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)




#delay_time = time.time() + 10
#
#while (time.time() < delay_time):
#
  #  GPIO.output(17, False)
 #   
#GPIO.output(17, True)
ConstantCurrent = 0
ConstantVoltage1 = 0
ConstantVoltage2 = 0
GND = 1
test = True

if (ConstantCurrent == 1):
    CC = True
    CV1 = True
    CV2 = True
    
if (ConstantVoltage1 == 1):
    CC = True
    CV1 = False
    CV2 = True
    
if (ConstantVoltage2 == 1):
    CC = False
    CV1 = False
    CV2 = True
    
if (GND == 1):
    CC = True
    CV1 = True
    CV2 = False
 
GPIO.output(17, CC)
GPIO.output(27, CV1)
GPIO.output(22, CV2)
GPIO.output(5, test)
GPIO.output(4, CC)
GPIO.output(6, CV1)
GPIO.output(13, CV2)
GPIO.output(19, test)
GPIO.output(16, CC)
GPIO.output(26, CV1)
GPIO.output(20, CV2)
GPIO.output(21, test)
GPIO.output(10, CC)
GPIO.output(9, CV1)
GPIO.output(11, CV2)
GPIO.output(8, test)




 



