from queue import Empty
import sqlite3 as sl
import userdata

class DatabaseManager(object):

    def __init__(self):
        self.con = sl.connect('stlDatabase.db')
        self.c = self.con.cursor()
        self.checkTables()
        self.mUserManager = userdata.UserManager(self.con,self.c)

    def checkTables(self):
        #mostly needed for first startup to create tables
        #USER Table -> stores userID and RegisterDate
        self.c.execute('create table if not exists "User" (id TEXT PRIMARY KEY , registered_at TEXT, FOREIGN KEY(id) REFERENCES login_date (id))')
        #INTERACTION Table -> stores interactions with DINA of a user
        self.c.execute('create table if not exists "interaction" (database_id INTEGER PRIMARY KEY AUTOINCREMENT,id TEXT, date TEXT)')
 

print("Creating Database entrys: ")
mDatabase = DatabaseManager()
print("..Done")

