import time
import psycopg2
import db4
import RPi.GPIO as GPIO
import dht114
import gpio_int4
import datetime

class Battery:
    
    try:
        #connect to the database
        connect_str = "dbname='ChargeData' user='postgres' host='127.0.0.1' " + \
                      "password='josephlorenzo'"
        conn = psycopg2.connect(connect_str)
    except: #if the connection is unsucessful
        print('Unable to connect to the database')
        
    cur = conn.cursor()
        
    def __init__(self, name,  number, relay1, relay2, relay3, testpin, temppin, voltpin, curpin):
        self.name = name
        self.number = int(number)
        self.relay1 = relay1
        self.relay2 = relay2
        self.relay3 = relay3
        self.testpin = testpin
        self.voltage = 0
        self.current = 0
        self.temperature = 0
        self.temppin = temppin
        self.humidity = 0
        self.delaytime = 0
        self.state = 0
        self.wait_time = 0
        self.voltpin = voltpin
        self.curpin = curpin
        
    def getreadings(self):
        self.current = gpio_int4.read_current(self.curpin) #get current
        gpio_int4.set_low(self.testpin)
        time.sleep(.1)
        self.voltage = gpio_int4.read_voltage(self.voltpin) #get voltage
        gpio_int4.set_high(self.testpin)
        sensorcombo = dht114.read_temp_humid(self.cur, self.temppin, self.temperature, self.humidity)  #get temp and humid combo from sensor
        self.temperature = sensorcombo[0]       #separate temperature
        self.humidity = sensorcombo[1]          #separate out humidity

        
    def updatedb(self):
        db4.updatedbval(self.cur, 'realtimedata', 'voltage', self.voltage, 'time', self.number) #update the db voltage
        db4.updatedbval(self.cur, 'realtimedata', 'temp', self.temperature, 'time', self.number)   #update the db temp
        db4.updatedbval(self.cur, 'realtimedata', 'humid', self.humidity, 'time', self.number) #update the db humidity
        db4.updatedbval(self.cur, 'realtimedata', 'current', self.current, 'time', self.number) #update the db humidity          
        
        self.conn.commit()


a = Battery('one', 1, 17, 27, 22, 5, 14, 0, 1)
b = Battery('two', 2, 4, 6, 13, 19, 15, 2, 3)
c = Battery('three', 3, 16, 26, 20, 21, 7, 4, 5)
d = Battery('four', 4, 10, 9, 11, 8, 12, 6, 7)

battery_list = [a, b, c, d]


while True:
    for Battery in battery_list:
        Battery.getreadings()
        Battery.updatedb()
        print(Battery.number)