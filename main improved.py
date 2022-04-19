# -*- coding: utf-8 -*-

import csv
import sys
import copy
import sqlite3 as sl

class DatabaseManager(object):
    def __init__(self):
        self.con = sl.connect('stlDatabase.db')
        self.c = self.con.cursor()
        self.checkTables()

    def checkTables(self):
        #mostly needed for first startup to create tables
        self.c.execute('create table if not exists "Tagungen" (name STRING PRIMARY KEY)')
        pass

class BlacklistReader(object):
    #Reads and Stores a List of Konferenzen that is just used internaly and or for testing purposes to keep the stats clean
    def __init__(self):
        self.blacklist = []
        self.readBlacklist()

    def readBlacklist(self):
        with open('interneTagungen.txt',encoding='utf-8') as f:
            for line in f:
                element = line.strip()
                self.blacklist.append(element)
        print ("%s interne Tagungen gefunden" % len(self.blacklist))

    def isInternal(self,name):
        if name.strip() in self.blacklist:
            return True
        else:
            return False

class Konferenz(object):
    def __init__(self):
        self.name = ""
        self.user = set()
        self.test = False
        self.portalpartner = ""
        self.creatorLan = ""
        self.internal = False

    def getUserNumber(self):
        return len(self.user)
#TODO use this
class Teilnehmer(object):
    def __init__(self):
        self.id = 0
        self.portalpartner = ""
        self.language = ""

class FilterListe(object):
    def __init__(self):
        konferenznamen =[]

mBlacklist = BlacklistReader()
mDatabase = DatabaseManager()

csv.field_size_limit(100000000) # increase limit so no crash happens
lastday = ""
Data  = []
currentDay =["",[],[]]
with open('data.csv',encoding='utf-8',newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    i = 0     
    for row in spamreader:
        #skip the first row just data headers
        if i != 0:
            #column #0 Date, column #1 Konferenzname, column #2 Portalpartner, column #3 Language, column #5 UserID
            # remove time only intrested in day
            day = row[0].split()[0]
            #check if day allready existis
            entryExists = False
            for datum in Data:
                if datum[0] == day:
                    #check if Konferenz allready exists or not
                    konferenzExists = False
                    for konferenz in datum[1]:
                        if konferenz.name == row[1].strip():
                            konferenz.user.add(row[5])
                            konferenzExists = True
                    if konferenzExists ==  False:
                        #create konferenz
                        mKonferenz = Konferenz()
                        mKonferenz.name = row[1].strip()
                        mKonferenz.portalpartner = row[2]
                        mKonferenz.creatorLan = row[3]
                        mKonferenz.user.add(row[5])
                        mKonferenz.internal = mBlacklist.isInternal(mKonferenz.name)
                        datum[1].append(mKonferenz)
                    entryExists = True
            if entryExists == False:
                #create conference
                mKonferenz = Konferenz()
                mKonferenz.name = row[1]
                mKonferenz.portalpartner = row[2]
                mKonferenz.creatorLan = row[3]
                mKonferenz.user.add(row[5])
                
                Data.append([day,[mKonferenz]])
        #Debug break
        #if i >= 50:
            #break 
        i+=1
#remove konferenzes with only 1 participant
for entry in Data:
    newList = []
    for konferenz in entry[1]:
        if len(konferenz.user) > 1:
            newList.append(konferenz)
        entry[1] = newList
#remove days without konferenzes ? 

#remove konferenzes marked internal
DataWithoutInternal = copy.deepcopy(Data)# new List in case comparison is wanted between data with internal removed and not removed
for entry in DataWithoutInternal:
    newList =[]
    for konferenz in entry[1]:
        if konferenz.internal == True:
            print ("%s entfernt da interne Tagung" % konferenz.name)
        else:
            newList.append(konferenz)
        entry[1] = newList

#write csv TODO: add routine for agregated montly data
print ("Writing .csv...")
with open('cleanData.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(["Datum","Gesamt Konferenzen","Konferenzen ohne Interne", "Anteil Interne Konferenzen an Gesamt",
    "Gesamt Nutzer:innen", "Nutzer:Innen ohne Interne", "Anteil Interne Nutzer:Innen an Gesamt"])
    for entry in DataWithoutInternal:
        konferenzcount = 0
        usercount = set()
        for konferenz in entry[1]:
            konferenzcount += 1
            usercount.update(konferenz.user)
        for element in Data: # also add the numbers of konferenzen with internal
            if element[0] == entry[0]:
                konferenzcountWithInternal = 0
                usercountWithInternal = set()
                for konferenzWithInternal in element[1]:
                    konferenzcountWithInternal += 1
                    usercountWithInternal.update(konferenzWithInternal.user)

        if konferenzcount  != 0:
            prozentKonferenzen = round((konferenzcountWithInternal-konferenzcount)/konferenzcountWithInternal*100,2)
            prozentUser =  round((len(usercountWithInternal)-len(usercount))/len(usercountWithInternal)*100,2)

            spamwriter.writerow([entry[0],konferenzcountWithInternal,konferenzcount,str(prozentKonferenzen) + "%",
            len(usercountWithInternal),len(usercount),str(prozentUser) + "%"]) 