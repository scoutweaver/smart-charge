import psycopg2
import datetime

try:
    #connect to the database
    connect_str = "dbname='ChargeData' user='postgres' host='127.0.0.1' " + \
                    "password='josephlorenzo'"
    conn = psycopg2.connect(connect_str)
except: #if the connection is unsucessful
    print('Unable to connect to the database')
    
cur = conn.cursor()

def CheckToptime(cur, conn, batt): #function to write trip the topoff value if it is time
    topit = 0
    cur.execute("SELECT toptime FROM topschedules WHERE batt = " + str(batt))
    toptime = cur.fetchone()
    #print(toptime)
    toptime = toptime[0]
    print(toptime)
    #print(toptime)
    nowtime = datetime.datetime.now()
    #print(nowtime)
    print(nowtime)
    timediff = toptime - nowtime
    print(timediff)
    timediffsec = datetime.timedelta.total_seconds(timediff) - 657570 - 1800
    #print(timediffsec, 'ppp')
    if (0 > timediffsec):
        topit = 1
    else:
        topit = 0
    #db4.updatedbval(cur, 'realtimedata', 'topoff', topit, 'time', batt)
    conn.commit()
    #print(topit, 'ooo')
    return topit, timediffsec

print(CheckToptime(cur, conn, 1))