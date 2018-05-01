import psycopg2
import functools
#take a full column from the table
def getcol(cur, tab, col):
    command = "SELECT " + col +" FROM " + tab
    cur.execute(command)
    collist = cur.fetchall()
    #translate list from db language to inegers
    collistint = []
    for n in range(0, len(collist)):
        collistint.append(functools.reduce(lambda rst, d: rst * 10 + d, (collist[n])))
    return collistint

#take a specific row and column value from table
def getcolval(cur, tab, col, num): 
    command = "SELECT " + col +" FROM " + tab
    cur.execute(command)
    collist = cur.fetchall()
    #trnslate from db language to inegers
    collistint = functools.reduce(lambda rst, d: rst * 10 + d, (collist[num-1]))
    return collistint

#Write to a specific roww and column in a table
def updatedbval(cur, tab, col, val, col2, time):
    cur.execute("UPDATE " + tab + " set " + col + " = " + str(val) + " where " + col2 + " = " + str(time))
    
def updatedbfsm(cur, val): #write the new fsm value to its table
    command = "UPDATE fsm set fsmvalue = " + str(val) + " where id = 1"
    cur.execute(command)

def newrow(cur, self, timer):
    #command = 'INSERT INTO ' + data + ' (' + cycle, voltage, temp, current ') VALUES (' + 0, 3, 3, 3 + ')'
    #cur.execute(command)
    sql = "INSERT INTO data(cycle, time, voltage, temp, current) VALUES(%s, %s, %s, %s, %s)"
    #datalist = (0, self.voltage, self.temperature, self.current)
    datalist = self.number,timer,self.voltage,self.temperature,self.current
    cur.execute(sql, datalist)
