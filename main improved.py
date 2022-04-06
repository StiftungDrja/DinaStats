# -*- coding: utf-8 -*-

import csv
import sys


class Konferenz(object):
    def __init__(self):
        self.name = ""
        self.user = set()
        self.test = False
        self.portalpartner = ""
        self.creatorLan = ""

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
        #if i >= 100:
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
#write csv
print ("Writing .csv...")
with open('cleanData.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(["Datum","Anzahl Konferenzen","Nutzer:innen"])
    for entry in Data:
        konferenzcount = 0
        usercount = set()
        for konferenz in entry[1]:
            #print (entry[0] + " " + konferenz.name)
            konferenzcount += 1
            usercount.update(konferenz.user)

        if konferenzcount  != 0:
            spamwriter.writerow([entry[0],konferenzcount,len(usercount)])