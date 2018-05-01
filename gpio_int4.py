import time
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)  #set the pin numbering system
GPIO.setwarnings(False) #stop displaying the warnings

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadcraw(adcnum, clockpin, mosipin, misopin, cspin):  #get the value (0-1024) from IC register
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)   #initialize pin value high

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

# the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(10, GPIO.OUT)
GPIO.setup(9, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)

def readadc(adcpin): #function to read the voltage on the ADC pin 'adcpin' (0-7)
    adc_raw_data = readadcraw(adcpin, SPICLK, SPIMOSI, SPIMISO, SPICS)
    return adc_raw_data # a value from 0 to 1024

def read_voltage(adcpin):   #converts the 1024 scaled number to a voltage
    adc_raw_data = readadc(adcpin)  #read the 1024 num
    #print(adc_raw_data)
    #print (adcpin)
    #print("old: ", adc_raw_data)
    if (adcpin == 0):
        adc_raw_data = adc_raw_data - 11
    elif (adcpin == 2):
        adc_raw_data = adc_raw_data - 18
    elif (adcpin == 4):
        adc_raw_data = adc_raw_data - 11
    elif (adcpin == 6):
        adc_raw_data = adc_raw_data - 13
    #print("new: ", adc_raw_data)
    percent_voltage = adc_raw_data / 1024  #get a percentage
    actual_voltage = 5.0 * percent_voltage  #get the 5.0V scale
    actual_voltage1 = actual_voltage / .2945
    #print(actual_voltage1)
    return actual_voltage1

def read_current(adcpin):   #converts the 1024 scaled number to a voltage
    adc_raw_data = readadc(adcpin)  #read the 1024 num
    #print (adcpin)
    #print("old: ", adc_raw_data)
    if (adcpin == 1):
        adc_raw_data = adc_raw_data + 1
    elif (adcpin == 3):
        adc_raw_data = adc_raw_data + 1
    elif (adcpin == 5):
        adc_raw_data = adc_raw_data + 1
    elif (adcpin == 7):
        adc_raw_data = adc_raw_data 
    #print("new: ", adc_raw_data)
    percent_voltage = adc_raw_data / 1024  #get a percentage
    actual_voltage = 5.066 * percent_voltage  #get the 5.0V scale
    actual_current = (actual_voltage-2.533)/.133
    #print(actual_current)
    return actual_current

def read_raw(adcpin):
    raw_data = readadc(adcpin)
    percent_voltage = raw_data / 1024  #get a percentage
    actual_voltage = 5.066* percent_voltage  #get the 5.0V scale
    return actual_voltage

def set_high(pinnum):
    GPIO.output(pinnum, True)
    
def set_low(pinnum):
    GPIO.output(pinnum, False)
    
a = read_current(1)

#print(a)
