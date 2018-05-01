#The Updated version with classes added

import time
import psycopg2
import db4
import RPi.GPIO as GPIO
import dht114
import gpio_int4
import datetime
timer = 0
class Battery:
    
    try:
        #connect to the database
        connect_str = "dbname='ChargeData' user='postgres' host='127.0.0.1' " + \
                      "password='josephlorenzo'"
        conn = psycopg2.connect(connect_str)
    except: #if the connection is unsucessful
        print('Unable to connect to the database')
    #define our cursor
    cur = conn.cursor()
    cur.execute("truncate data;")
    hold80 = 15.53
    #hold80 = 14.7
    topoffgoal = 16
    minvolt = 10
    maxvolt = 18
    
    def __init__(self, name,  number, relay1, relay2, relay3, testpin, temppin, voltpin, curpin):
        self.name = name
        self.number = int(number)
        self.relay1 = relay1
        self.relay2 = relay2
        self.relay3 = relay3
        self.testpin = testpin
        self.voltage = 0
        self.current = 0
        self.charge_signal = 0
        self.temperature = 0
        self.temppin = temppin
        self.humidity = 0
        self.delaytime = 0
        self.state = 0
        self.topping = 0
        self.volt_log = [0]
        self.wait_time = 0
        self.faults = [0,0,0,0,0,0,0,0,0,0]
        self.faulted = 0
        self.voltpin = voltpin
        self.curpin = curpin
        self.errhigh = 0
        self.errlow = 0

        
    def initialization(self):
        self.volt_log = [0]
        #db4.updatedbfsm(self.cur, 0, self.number)    #start the fsm in th initial state
        #initilizing the finished indicator to 0 in db
        db4.updatedbval(self.cur, 'realtimedata', 'finfin', 0, 'time', 1)
        db4.updatedbval(self.cur, 'realtimedata', 'topoff', 0, 'time', 1)
        self.state = 0
        self.conn.commit()
        #initializing the faults in the db to 0
        
    def getreadings(self):
        #print("----------------")
        #print("battery: ", self.number)
        newcurrent = gpio_int4.read_current(self.curpin) #get current
        #print(newcurrent)
        #currentdifference = abs(newcurrent - self.current)
        #print("newcurrent: ", newcurrent)
        if (.1 < newcurrent < .19):
            self.current = .15
        elif (-.04 < newcurrent < .04):
            self.current = 0
            #print("error!!!!")
        else:
            self.current = newcurrent
        
        #print("selfcurrent: ", self.current)
        sensorcombo = dht114.read_temp_humid(self.cur, self.temppin, self.temperature, self.humidity)  #get temp and humid combo from sensor
        self.temperature = sensorcombo[0]       #separate temperature
        #print("temp",self.temperature)
        self.humidity = sensorcombo[1]          #separate out humidity
        gpio_int4.set_low(self.testpin)
        time.sleep(.15)
        newvolt = gpio_int4.read_voltage(self.voltpin) #get voltage
        voltdiff = newvolt-self.voltage
        voltdifference = abs(voltdiff)
        if (.07 > voltdifference):
            self.voltage = newvolt
            self.errhigh = 0
            self.errlow = 0
        elif (-1 < newvolt < 1):
            self.voltage = 0
            self.errhigh = 0
            self.errlow = 0
        elif (self.voltage == 0):
            self.voltage = newvolt
            self.errhigh = 0
            self.errlow = 0
        elif (.07 < voltdifference):
            if (voltdiff > 0):
                self.errhigh = self.errhigh+1
                if (self.errhigh == 5):
                    self.voltage = newvolt
                    self.errhigh = 0
                    self.errlow = 0
            if (voltdiff < 0):
                self.errlow = self.errlow+1
                if (self.errlow == 5):
                    self.voltage = newvolt
                    self.errlow = 0
                    self.errhigh = 0
        #if (newvolt < 18):
        #    self.voltage = newvolt
        gpio_int4.set_high(self.testpin)
        #time.sleep(.1)

        #print ("---------------")
        
    def checkfaults(self):
        #Fault Key
        #2: Low Voltage
        #3: High Voltage
        #4: High Temperature
        #5: Low Temperature
        #6: Negative Voltage
        #7: Short
        #8: Break
        #9: High Humidity
        #0: Reset
        self.faults = [0,0,0,0,0,0,0,0,0] 
        if (self.temperature > 50):
            self.faults[3] = 1
        elif (self.temperature < 15):
            self.faults[4] = 1
        if (self.humidity > 94):
            self.faults[8] = 1
        if (self.voltage < 0):
            self.faults[5] = 1
        elif (self.voltage < self.minvolt):
            self.faults[1] = 1
        elif (self.voltage > self.maxvolt):
            self.faults[2] = 1
        if sum(self.faults) == 0:    #no faults tripped
            self.faulted = 0
        else:
            self.faulted = 1
        

    def updatedb(self):
        db4.newrow(self.cur, self, timer)
        db4.updatedbval(self.cur, 'realtimedata', 'voltage', self.voltage, 'time', self.number) #update the db voltage
        db4.updatedbval(self.cur, 'realtimedata', 'current', self.current, 'time', self.number)
        db4.updatedbval(self.cur, 'realtimedata', 'temp', self.temperature, 'time', self.number)   #update the db temp
        db4.updatedbval(self.cur, 'realtimedata', 'humid', self.humidity, 'time', self.number) #update the db humidity
        db4.updatedbval(self.cur, 'faults', 'lowvoltage', self.faults[1], 'id', self.number)
        db4.updatedbval(self.cur, 'faults', 'highvoltage', self.faults[2], 'id', self.number)
        db4.updatedbval(self.cur, 'faults', 'hightemp', self.faults[3], 'id', self.number)
        db4.updatedbval(self.cur, 'faults', 'lowtemp', self.faults[4], 'id', self.number)
        db4.updatedbval(self.cur, 'faults', 'negativevoltage', self.faults[5], 'id', self.number)
        db4.updatedbval(self.cur, 'faults', 'highhumid', self.faults[8], 'id', self.number)
        if (self.state == 4):
            db4.updatedbval(self.cur, 'realtimedata', 'finfin', 1, 'time', self.number)
        else:
            db4.updatedbval(self.cur, 'realtimedata', 'finfin', 0, 'time', self.number)            
        self.conn.commit()
        
    def execute(self):
        if (self.faulted == 1):
            self.charge_signal = 3
            Send_charge(self.charge_signal, self)
            self.state = 0
            db4.updatedbval(self.cur, 'realtimedata', 'current', self.current, 'time', self.number)
            self.conn.commit()
            
        elif ( self.delaytime < time.time() ):
            topcheck = CheckToptime(self.cur, self.conn, self.number)
            self.topping = topcheck[0]
            self.wait_time = topcheck[1]
            #print(self.number, self.wait_time)
            if (self.topping == 1):
                if (self.state == 2):
                    self.state = 3
            if (self.state == 4):
                if (self.voltage < 5.53):
                    self.state = 0
            a = checkvoltage(self.voltage, self.state, self.hold80, self.topoffgoal)
            self.state = a[1]
            self.delaytime = a[2]
            self.charge_signal = a[0]
            Send_charge(self.charge_signal, self)
            db4.updatedbval(self.cur, 'realtimedata', 'current', self.current, 'time', self.number)
            self.conn.commit()
            if(self.number == 1):
                self.volt_log.append(self.voltage)
                #print (self.volt_log)
                #print('State: ', self.state)
                #print('Voltage: ', self.voltage)
                #print('Current: ', self.current)
                #print('Temperature: ', self.temperature)
                #print('Humidity: ', self.humidity)
                #print('Time until topoff: ', self.wait_time)
                #print('Topoff trip: ', self.topping)
                #print('-----------------------------')
                
            
            
                
def checkvoltage(battvolt, battstate, hold80, topoffgoal):
    VS = 0
    newstate = 0
    newdelay = 0
    if (battstate == 1 or battstate == 0):
        if (battvolt > hold80):
            VS = 1
            newstate = 2
            newdelay = time.time() + 20
        else:
            VS = 0
            newstate = 1
            newdelay = time.time() + 20
    elif (battstate == 2):
        VS = 1
        newstate = 2
        newdelay = time.time() + 20
    elif (battstate == 3):
        if (battvolt > topoffgoal):
            VS = 2
            newstate = 4
            newdelay = time.time() + 20
        else:
            VS = 2
            newstate = 3
            newdelay = time.time() + 20
    elif (battstate == 4):
        VS = 2
        newstate = 4
        newdelay = time.time() + 20
        print('DONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            
    return (VS, newstate, newdelay)
        
def CheckToptime(cur, conn, batt): #function to write trip the topoff value if it is time
    topit = 0
    cur.execute("SELECT toptime FROM topschedules WHERE batt = " + str(batt))
    toptime = cur.fetchone()
    #print(toptime)
    toptime = toptime[0]
    #print(toptime)
    nowtime = datetime.datetime.now()
    #print(nowtime)
    timediff = toptime - nowtime
    timediffsec = datetime.timedelta.total_seconds(timediff)  - 657570 - 1800
    #print(timediffsec, 'ppp')
    if (0 > timediffsec):
        topit = 1
    else:
        topit = 0
    db4.updatedbval(cur, 'realtimedata', 'topoff', topit, 'time', batt)
    conn.commit()
    #print(topit, 'ooo')
    return topit, timediffsec
##    else:
##        print ("Seconds until next topoff: " + str(timediffsec))
##        #print (" ")
        
def Send_charge(charge_signal, self):
    if (charge_signal == 0):    #relay binary 111: constant current mode
        gpio_int4.set_high(self.relay1)
        gpio_int4.set_high(self.relay2)
        gpio_int4.set_high(self.relay3)
    elif (charge_signal == 1):   #relay binary 101: constant voltage 1 mode
        gpio_int4.set_high(self.relay1)
        gpio_int4.set_low(self.relay2)
        gpio_int4.set_high(self.relay3)
    elif (charge_signal == 2):   #relay binary 001: constant voltage 2 mode
        gpio_int4.set_low(self.relay1)
        gpio_int4.set_low(self.relay2)
        gpio_int4.set_high(self.relay3)
    elif (charge_signal == 3):   #relay binary xx0 (110 by default): grounding mode
        gpio_int4.set_high(self.relay1)
        gpio_int4.set_high(self.relay2)
        gpio_int4.set_low(self.relay3)
    
        
a = Battery('one', 1, 17, 27, 22, 5, 14, 0, 1)
b = Battery('two', 2, 4, 6, 13, 19, 15, 2, 3)
c = Battery('three', 3, 16, 26, 20, 21, 7, 4, 5)
d = Battery('four', 4, 10, 9, 11, 8, 15, 6, 7)

battery_list = [a, b, c, d]


for Battery in battery_list:
    Battery.initialization()

while True:
    for Battery in battery_list:
        Battery.getreadings()
        Battery.checkfaults()
        Battery.updatedb()
        Battery.execute()
        timer = timer + 1
        #if (Battery.number == 1):
            #print(Battery.number, Battery.voltage, Battery.current, Battery.temperature, Battery.state)
            #print(Battery.faulted)
            #print(Battery.delaytime)
            #print(time.time())
        