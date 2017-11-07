import smart
import time
import psycopg2
import db

#----------------------------------Database Setup------------------------------------
#test for github
try:
    #connect to the database
    connect_str = "dbname='ChargeData' user='postgres' host='127.0.0.1' " + \
                  "password='josephlorenzo'"
    conn = psycopg2.connect(connect_str)
except: #if the cannection is unsucessful
    print('Unable to coneect to the database')
#define our cursor
cur = conn.cursor()

#take a full row from the table
#listdata = db.getcolval(cur, 'faults', 'id', 1)
#listdata = db.getcol(cur, 'faults', 'id')
#db.updatedbval1(cur, 'data', 'current', '1.1', 'time', Time)
i = 1
while i < 8:
    db.updatedbval(cur, 'faults', 'trip', 0, 'id', i)
    i = i+1
db.updatedbval(cur, 'realtimedata', 'current', 0, 'time', 1)
#---------------------------Plug in test(fsm = 0)-------------------------------------
def plugtest():
    print('in plug in test state')
    if (smart.CheckFault(cur) != 0):
        db.updatedbfsm(cur, 4)
        conn.commit()
    else:
        db.updatedbfsm(cur, 1)
        conn.commit()
Time = 1
#---------------------------Initial Charging of the Battery(fsm = 1)-----------------
def charging():
    print('in charging state')
    if (smart.finishC == 0):
        starttime = time.time()                        #determine the start time to base others off of
        Current = smart.OutputCurrent(cur, Time, conn)   #Calculate output current and test for faults   
        print ('Current = ',Current)           #Send the output current value
        db.updatedbval(cur, 'realtimedata', 'current', Current, 'time', 1)
        conn.commit()
        #send current signal from db to pin
    else:
        db.updatedbfsm(cur, 2)
        conn.commit()
        
#-----------------------------------Wait for discharge(fsm = 2)----------------------------
def dischargewait():
    print('in discharge state')
    time.sleep(20)
    if (smart.getVolt(cur, Time) < 2.8):
        db.updatedbfsm(cur, 1)
        conn.commit()
    else:
        db.updatedbfsm(cur, 2)
        conn.commit()
    
#------------------------------------Top off system(fsm = 3)------------------------------
def topoff():
    print('in topoff state')
    Current = smart.TopCurrent(cur, Time, conn)      #Calculate output current and test for faults
    print('Current = ' + str(Current))
    db.updatedbval(cur, 'realtimedata', 'current', Current, 'time', 1)
    conn.commit()
    #send current signal from db to pin
    if (smart.finishT == 2):
        db.updatedbfsm(cur, 5)
        conn.commit()

#----------------------------------Fault Detected(fsm = 4)--------------------------------------
def faultdetected():
    print('in fault detected state')
    retest = 'n'
    while retest != 'y':
        retest = input('Would you like to retest the faults? (y/n) ')
    i = 1
    while i < 8:
        db.updatedbval(cur, 'faults', 'trip', 0, 'id', i)
        i = i+1
    db.updatedbval(cur, 'faults', 'trip', 0, 'id', 1)
    db.updatedbfsm(cur, 0)
    conn.commit()
    
#----------------------------------fsm definitions----------------------------------------
fsmvalue = db.getcolval(cur, 'fsm', 'fsmvalue', 1)
fsm = {0 : plugtest,
       1 : charging,
       2 : dischargewait,
       3 : topoff,
       4 : faultdetected}

run = 'n'
while run != 'y':
    run = input('Start a charge cycle? (y/n):  ')
    
db.updatedbfsm(cur, 0)
conn.commit()

while True:
    ready = 'n'
    while ready != 'y':
        voltage = input('whats the voltage? ')
        temp = input('whats the temperature? ')
        humid = input('whats the humidity? ')
        topoff = input('you ready to top off? (y/n) ')
        ready = input('proceed? (y/n) ')
    if topoff == 'y':
        db.updatedbfsm(cur, 3)
        conn.commit()
    db.updatedbval(cur, 'realtimedata', 'voltage', voltage, 'time', 1)
    conn.commit()
    db.updatedbval(cur, 'realtimedata', 'temp', temp, 'time', 1)
    conn.commit()
    db.updatedbval(cur, 'realtimedata', 'humid', humid, 'time', 1)
    conn.commit()
    
    test = smart.OutputCurrent(cur, Time, conn)
    
    if (smart.CheckFault(cur) != 0):
        #t = smart.Readfaults(cur)
        #print(t)
        print("Faults are tripped! ", smart.Readfaults(cur))
        db.updatedbfsm(cur, 4)
        conn.commit()
    elif (smart.finishT == 2):
        db.updatedbfsm(cur, 5)
        conn.commit()
    fsmvalue = db.getcolval(cur, 'fsm', 'fsmvalue', 1)
    print(smart.finishT)
    if (fsmvalue == 5):
        break
    fsm[fsmvalue]()
    time.sleep(5)


print ('Finished!')