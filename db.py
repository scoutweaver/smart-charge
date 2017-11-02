import psycopg2
import functools
#take a full column from the table
def getcol(cur, tab, col):
    command = "SELECT " + col +" FROM " + tab
    cur.execute(command)
    collist = cur.fetchall()
    
    collistint = []
    for n in range(0, len(collist)):
        collistint.append(functools.reduce(lambda rst, d: rst * 10 + d, (collist[n])))
    return collistint

def getcolval(cur, tab, col, num):
    command = "SELECT " + col +" FROM " + tab
    cur.execute(command)
    collist = cur.fetchall()
    collistint = functools.reduce(lambda rst, d: rst * 10 + d, (collist[num-1]))
    return collistint

def updatedbval(cur, tab, col, val, col2, time):
    
    #command = "UPDATE " + tab + " set " + col + " = " + val + " where " + col2 + " = " + time
    cur.execute("UPDATE " + tab + " set " + col + " = " + str(val) + " where " + col2 + " = " + str(time))
    
def updatedbfsm(cur, val):
    command = "UPDATE fsm set fsmvalue = " + str(val) + " where id = 1"
    cur.execute(command)
    
def writedbval1(cur, tab, col, val):
    cur.execute("INSERT INTO data (current) VALUES (1.1)")