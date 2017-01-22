import sqlite3

conn = sqlite3.connect('usr.db')
print "Opened database successfully"

conn.execute('''CREATE TABLE AUTH
       (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
       USERID           TEXT    NOT NULL,
       AID			  TEXT    NOT NULL,	
       PASSWORD       CHAR(50) NOT NULL);
       ''')

print "Table created successfully"

conn.close()	