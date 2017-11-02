import db
#This contains all the functions used in the Smart Charge system
Fault = 0
finish = 0
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
    elif (Temperature<0):
        db.updatedbval(cur, 'faults', 'trip', 1, 'id', 4)
        conn.commit()
        TD = 0
    elif (Temperature > 50):
        db.updatedbval(cur, 'faults', 'trip', 1, 'id', 3)
        conn.commit()
        TD = 0
    return TD

#Adjusting Current according to voltage
def VoltageDiff(Voltage, cur, conn):
    VD = 1.0                             #decimal current multiplier
    if (0<=Voltage<3):                    #operation from 0 to 80% capacity
        VD = 1.0
    elif (Voltage<0):
        VD = 0                           #no current bc of fault
        db.updatedbval(cur, 'faults', 'trip', 1, 'id', 5)
        conn.commit()
    elif (Voltage > 4.5):
        db.updatedbval(cur, 'faults', 'trip', 1, 'id', 2)
        conn.commit()
    elif (3<=Voltage):                   #no current until top off
        VD = 0
        global finish
        finish = 1
    return VD
        
#Computing the output current from voltage and temperature  
def OutputCurrent(cur, Time, conn): 
    Current = 1*TempDiff(getTemp(cur, Time), cur, conn)*VoltageDiff(getVolt(cur, Time), cur, conn)  
    return Current

#Checks to see if there is a fault being triggered
def CheckFault(cur):
    listdata = db.getcol(cur, 'faults', 'trip')
    if sum(listdata) == 0:
        Faults = 0
    else:
        Faults = 1
    return Faults                   #Gets the fault indicator from the DB

def ToppffCurrent(cur, Time, conn): 
    Current = 1.1*TempDiff(getTemp(cur, Time),cur, conn)*VoltageDiff(getVolt(cur, Time), cur, conn)
    if (getVolt(cur, Time)>3.2):
        global finish
        finish = 2
    return Current

def Readfaults(cur):
    cur.execute("SELECT definition FROM faults WHERE trip = 1")
    faults = cur.fetchall()
    return faults


