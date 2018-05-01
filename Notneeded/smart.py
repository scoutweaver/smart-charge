import db
import datetime
import time

#define the global variables
Fault = 0
finishT = 0
finishC = 0

#Retreiveing the temperature
def getTemp(cur, Time):
    Temp = db.getcolval(cur, 'realtimedata', 'temp', Time)
    return Temp

#Retreiveing Voltage
def getVolt(cur, Time):
    Volt = db.getcolval(cur, 'realtimedata', 'voltage', Time)
    return Volt

#Adjusting Current according to temperature
def TempDiff(Temperature, cur, conn):
    TD = 1.0                             #decimal current multiplier
    if (0<=Temperature<=10):             #low end operating region
        TD = Temperature/10
    elif (10 < Temperature <= 35):       #normal operating region
        TD = 1
    elif (35 < Temperature <= 50):       #high end operating region
        TD = 1-((Temperature-35)/15)
    elif (Temperature<0):                #below permitable level
        db.updatedbval(cur, 'faults', 'trip', 1, 'id', 4) #trip fault
        conn.commit()
        TD = 0
    elif (Temperature > 50):             #above permitable level
        db.updatedbval(cur, 'faults', 'trip', 1, 'id', 3) #trip fault
        conn.commit()
        TD = 0
    return TD

#Adjusting Current according to voltage
def VoltageDiff(Voltage, cur, conn):
    VD = 1.0                             #decimal current multiplier
    if (0.1<=Voltage<3):                    #operation from 0 to 80% capacity
        VD = 1.0
    elif (Voltage<0.1):
        VD = 0                           #no current bc of fault
        db.updatedbval(cur, 'faults', 'trip', 1, 'id', 5) #trip fault
        conn.commit()
    elif (Voltage > 3.8):                #voltage should never be this high
        db.updatedbval(cur, 'faults', 'trip', 1, 'id', 2) #trip fault
        conn.commit()
    elif (3<=Voltage):                   #no current until top off
        if (finishT != 2):
            VD = 0
            global finishC                   #tell global that battery is ready for top off
            finishC = 1
        else:
            VD = 1.0
    return VD
        
#Computing the output current from voltage and temperature  
def OutputCurrent(cur, Time, conn): #basically 1 times the multipliers defined above
    Current = 1*TempDiff(getTemp(cur, Time), cur, conn)*VoltageDiff(getVolt(cur, Time), cur, conn)
    return Current

#Checks to see if there is a fault being triggered
def CheckFault(cur, Time):
    if (db.getcolval(cur, 'realtimedata', 'humid', Time) < 10000):  #if humidity is ok
        db.updatedbval(cur, 'faults', 'trip', 0, 'id', 8)   #set trip to 0
    else:
        db.updatedbval(cur, 'faults', 'trip', 1, 'id', 8)    #set trip to 1

    listdata = db.getcol(cur, 'faults', 'trip') #get a list of all fault trips
    if sum(listdata) == 0:    #no faults tripped
        Faults = 0
    else:
        Faults = 1            #at least one fault tripped
    return Faults             

def TopCurrent(cur, Time, conn): #takes the current all the way to max
    Current = 1.1*TempDiff(getTemp(cur, Time),cur, conn)*VoltageDiff(getVolt(cur, Time), cur, conn)
    print(getVolt(cur,Time))
    if (getVolt(cur, Time)>3.1):  #if completely charged
        global finishT     #trip global finish variable
        finishT = 2
        print("smart finishT = " + str(finishT))
    return Current        

def Readfaults(cur): #tells user exactly what faults were tripped
    cur.execute("SELECT definition FROM faults WHERE trip = 1")
    faults = cur.fetchall()
    return faults

def CheckToptime(cur, conn, batt, time): #function to write trip the topoff value if it is time
    cur.execute("SELECT toptime FROM topschedules WHERE batt = " + str(batt))
    toptime = cur.fetchone()
    toptime = toptime[0]
    #print(toptime)
    nowtime = datetime.datetime.now()
    #print(nowtime)
    timediff = toptime - nowtime
    timediffsec = datetime.timedelta.total_seconds(timediff)
    if 0 < timediffsec < 100:
        db.updatedbval(cur, 'realtimedata', 'topoff', 1, 'time', 1)
    else:
        print ("Seconds until next topoff: " + str(timediffsec))
        #print (" ")