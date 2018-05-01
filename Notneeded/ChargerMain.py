import smart
import time
import psycopg2
import db
import RPi.GPIO as GPIO
import dht11
import gpio_int
import datetime

#----------------------------------Database Setup------------------------------------
try:
    #connect to the database
    connect_str = "dbname='ChargeData' user='postgres' host='127.0.0.1' " + \
                  "password='josephlorenzo'"
    conn = psycopg2.connect(connect_str)
except: #if the connection is unsucessful
    print('Unable to connect to the database')
#define our cursor
cur = conn.cursor()
print (cur)
#initilizing the finished indicator to 0 in db
db.updatedbval(cur, 'realtimedata', 'finfin', 0, 'time', 1)
db.updatedbval(cur, 'realtimedata', 'topoff', 0, 'time', 1)
#initializing the faults in the db to 0
i = 1
while i < 9:    #all 8 faults in db
    db.updatedbval(cur, 'faults', 'trip', 0, 'id', i)
    i = i+1
db.updatedbval(cur, 'realtimedata', 'current', 0, 'time', 1)   #initialize charge current to 0


#---------------------------Plug in test(fsm = 0)-------------------------------------
def plugtest():     #function to test the battery health before any current applied
    print('in plug in test state')
    if (smart.CheckFault(cur, Time) != 0):   #if any faults detected
        db.updatedbfsm(cur, 4)         #go to fault detected state of fsm
        db.updatedbval(cur, 'realtimedata', 'current', 0, 'time', 1)
        db.updatedbval(cur, 'realtimedata', 'current', 0, 'time', 2)
        db.updatedbval(cur, 'realtimedata', 'current', 0, 'time', 3)
        db.updatedbval(cur, 'realtimedata', 'current', 0, 'time', 4)
        conn.commit()                  #save vaule in db
    else:
        db.updatedbfsm(cur, 1)         #else, go to the charging state 
        conn.commit()
Time = 1                               #using later for tracking charge cycle as  whole


#---------------------------Initial Charging of the Battery(fsm = 1)-----------------
def charging():                        #main charging mechanism for battery
    print('in charging state')
    if (smart.finishC == 0):                 #if the battery has not reached safe capacity                 #determine the start time to base others off of
        Current = smart.OutputCurrent(cur, Time, conn)   #Calculate output current  
        #print ('Current = ',Current)           
        db.updatedbval(cur, 'realtimedata', 'current', Current, 'time', 1) #send current value to db
        db.updatedbval(cur, 'realtimedata', 'current', Current, 'time', 2) #send current value to db
        db.updatedbval(cur, 'realtimedata', 'current', Current, 'time', 3) #send current value to db
        db.updatedbval(cur, 'realtimedata', 'current', Current, 'time', 4) #send current value to db
        conn.commit()
        #send current signal from db to pin
    else:
        db.updatedbval(cur, 'realtimedata', 'current', 0, 'time', 1)
        db.updatedbfsm(cur, 2)               #if the battery has reached safe capacity, move fsm to 2
        conn.commit()
        
#-----------------------------------Wait for discharge(fsm = 2)----------------------------
def dischargewait():        #this is idling unless the battery passively drains below a certain voltage
    print('in discharge state')
    voltnow = smart.getVolt(cur, Time)
    if (voltnow < 2.7):   #if, after 20 sec, voltage is below 2.8
        db.updatedbfsm(cur, 1)                #go back to charging state
        conn.commit()
        smart.finishC = 0
    else:
        time.sleep(20)           # wait 20 second in between checkups
        db.updatedbfsm(cur, 2)             #if it is still charge, then repeat this state
        conn.commit()
    
#------------------------------------Top off system(fsm = 3)------------------------------
def topoff():     #invoked when the user wants a topoff for battery use
    print('in topoff state')
    Current = smart.TopCurrent(cur, Time, conn)      #Calculate output current
    #print('Current = ' + str(Current))
    db.updatedbval(cur, 'realtimedata', 'current', Current, 'time', 1)  #update current in the db
    db.updatedbval(cur, 'realtimedata', 'current', Current, 'time', 2)  #update current in the db
    db.updatedbval(cur, 'realtimedata', 'current', Current, 'time', 3)  #update current in the db
    db.updatedbval(cur, 'realtimedata', 'current', Current, 'time', 4)  #update current in the db
    conn.commit()
    #send current signal from db to pin
    if (smart.finishT == 2):     #if the top off is complete
        db.updatedbfsm(cur, 5)   #move on to the finished state (5)
        conn.commit()

#----------------------------------Fault Detected(fsm = 4)--------------------------------------
def faultdetected():     #moves here when a fault is detected and stays until cleared and retested
    print('in fault detected state')
    retest = 'n'     
    while retest != 'y':                 #wait for retest request from user
        retest = input('Would you like to retest the faults? (y/n) ')
    i = 1
    while i < 9:     #reset all 8 faults to 0
        db.updatedbval(cur, 'faults', 'trip', 0, 'id', i)
        i = i+1
    db.updatedbfsm(cur, 0) #return to initial testing state
    conn.commit()
    
#----------------------------------fsm definitions----------------------------------------
fsmvalue = db.getcolval(cur, 'fsm', 'fsmvalue', 1)  #this is the state value in the db
fsm = {0 : plugtest,  #all these are defined above
       1 : charging,
       2 : dischargewait,
       3 : topoff,
       4 : faultdetected}



run = 'n'

finishC = 0
while run != 'y':   #wait for user to start the charging cycle
    run = input('Start a charge cycle? (y/n):  ')
    
db.updatedbfsm(cur, 0)    #start the fsm in th initial state
conn.commit()

while True:    #main fsm handling function
    dht11.readwrite(cur, Time)  #reads all sensor inputs and writes values to the db
    conn.commit()
    
    test = smart.OutputCurrent(cur, Time, conn)    #run a quick test for intial fault detection
    smart.CheckToptime(cur, conn, 1, time)
    topoff = db.getcolval(cur, 'realtimedata', 'topoff', Time) # see if we need to top off
    if (topoff == 1 and smart.finishT != 2):
        db.updatedbfsm(cur, 3)  #if so, then go to top off state
            

    
    if (smart.CheckFault(cur, Time) != 0):               #see if fault in db  is tripped
        print("Faults are tripped! ", smart.Readfaults(cur)) #tell user the specific fault
        db.updatedbval(cur, 'realtimedata', 'current', 0, 'time', 1)  #update current in the db
        conn.commit()
        db.updatedbfsm(cur, 4)     #send fsm to the fault state to wait for restesting
        conn.commit()
    elif (smart.finishT == 2):    #once faults are cleared, see if top off is done
        db.updatedbfsm(cur, 5)    #go to finish state 
        conn.commit()
    fsmvalue = db.getcolval(cur, 'fsm', 'fsmvalue', 1)   #updae the local fsm state from db
    if (fsmvalue == 5):    #if in finish state, then break the loop
        break
    fsm[fsmvalue]()   #preform the fs state function defined earlier
    #print('Temperature: ' + str(db.getcolval(cur, 'realtimedata', 'temp', 1)))
    print('Voltage: ' + str(db.getcolval(cur, 'realtimedata', 'voltage', 1)))
    print('Current: ' + str(db.getcolval(cur, 'realtimedata', 'current', 1)))
    print('Topoff: ' + str(db.getcolval(cur, 'realtimedata', 'topoff', 1)))
    print('-----------')

db.updatedbval(cur, 'realtimedata', 'finfin', 1, 'time', 1)
conn.commit()
print ('Finished!')   #all done!