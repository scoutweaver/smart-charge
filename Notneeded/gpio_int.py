import time
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


def readadc(adcpin): #function to read the voltage on the ADC pin 'adcpin' (0-7)
    adc_raw_data = readadcraw(adcpin, SPICLK, SPIMOSI, SPIMISO, SPICS)
    return adc_raw_data # a value from 0 to 1024

def read_voltage(adcpin):   #converts the 1024 scaled number to a voltage
    adc_raw_voltage = readadc(adcpin)  #read the 1024 num
    percent_voltage = adc_raw_voltage / 1024  #get a percentage
    actual_voltage = 5.0 * percent_voltage  #get the 5.0V scale
    return actual_voltage


