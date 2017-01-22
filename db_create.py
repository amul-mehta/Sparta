import sqlite3

conn = sqlite3.connect('user.db')
print "Opened database successfully"

conn.execute('''CREATE TABLE AUTH
       (ID INT PRIMARY KEY     NOT NULL,
       NAME           TEXT    NOT NULL,
       AID			  TEXT    NOT NULL,	
       PASSWORD       CHAR(50) NOT NULL);
       ''')

print "Table created successfully"

conn.close()	