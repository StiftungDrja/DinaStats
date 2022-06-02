import datetime
import glob
import csv
import sqlite3 

class UserManager(object):
    def __init__(self,con,c):
        self.con = con
        self.c = c
        self.filereader()

    def filereader(self):
        #reads the user-activity-report[...].csv file 
        activityReport = glob.glob('user-activity-report*')  
        with open(activityReport[0],encoding='utf-8',newline='') as csvfile:
            userreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            #colum 0 = id
            #colum 7 = latest login
            #colum 9 = registred at

            i = 0
            for row in userreader:
                if i != 0:#ignore first row (table headers)
                    if self.userHashExist(row[0]) == False: #create user if not allready in database
                        self.createUser(row[0],row[9])
                    #update users login
                    self.updateInteraction(row[0],row[7],"User-Activity")

                i +=1
        #also read bbb-rooms visit, for more user interactions 
        BBBRoomVisits = glob.glob('bbb-room-visits*')
        with open(BBBRoomVisits[0],encoding="utf-8",newline='') as csvfile:      
            bbbroomreader = csv.reader(csvfile,delimiter=',',quotechar='"')
            i = 0
            for row in bbbroomreader:
                if i != 0:
                    #colum 6 = id
                    #colum 0 = date
                    self.updateInteractionNoTransform(row[6],row[0].split()[0],"BBB-Room-Visits")
                i +=1

    def userHashExist(self,id):
        #check if a hash exists in the Database, returns true if a user exist, false if not
        with self.con:
            self.c.execute("SELECT rowid FROM User WHERE id LIKE ?",[id]) 
            data = self.c.fetchall()   
        if not data:
            return False
        else:
            return True

    def userInteractionExists(self,id,interactionDate):
        with self.con:
            self.c.execute("SELECT rowid FROM interaction WHERE id LIKE ? AND date LIKE ? ",(id,interactionDate))
            data = self.c.fetchall()
        if not data:
            return False
        else:
            return True
               
    def createUser (self,id,registerd_at):
        #creates a user in the database
        if self.userHashExist(id) == False:
            with self.con:
                try: 
                    self.c.execute("INSERT INTO User (Id,registered_at) Values (?,?)",(id,registerd_at.split()[0]))   
                except sqlite3.IntegrityError:
                    self.c.execute("SELECT rowid FROM USER WHERE id LIKE ?",[id])
                    data = self.c.fetchall()  
                    print ("Error for ID (duplicate): {0} ".format(id))
                    print(data)  
        else: 
            print ("User {0} allready exists".format(id))
       
    def updateInteraction(self,id,interaction_date,source):
        #create table for storing login times
        if self.userInteractionExists(id,self.LastLoginToDate(str(interaction_date))) == False: #no entry create 
            with self.con:            
                self.c.execute("INSERT INTO interaction(id,date,Source) Values (?,?,?)",(id,self.LastLoginToDate(str(interaction_date)),source))
        else:
            pass

    def updateInteractionNoTransform(self,id,interaction_date,source):
        #create table for storing login times
        if self.userInteractionExists(id,interaction_date) == False: #no entry create 
            with self.con:            
                self.c.execute("INSERT INTO interaction(id,date,Source) Values (?,?,?)",(id,interaction_date,source))
        else:
            pass
                    
    def LastLoginToDate(self,interaction_date):
        #Logins are stored as Dates since last Login, for the database we need a date in
        #YYYY-MM-DD
        #current date
        currentDate = datetime.date.today()
        days = datetime.timedelta(days=(int(interaction_date)))
        return currentDate - days

