#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 20:40:53 2017

@author: holomorfo
"""

# TODO: Transform midiutils to music21 

import csv
#import time

def saveCsv(fileName,midiTup):
    ''' Save a midi tupple as CSV
        Format ['Tick']  + ['Track']+ ['Chan']+['Type']+ ['Note']+ ['Vel']
    '''
    with open(fileName, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Tick']  + ['Track']+ ['Chan']+['Type']+ ['Note']+ ['Vel'])
        for k in midiTup:
            spamwriter.writerow(k)

def saveDursCsv(filename,durationList):
    ''' Save a midi tupple with duration as CSV
        Format ['Tick']  +['Dur']  + ['Track']+ ['Chan']+['Type']+ ['Note']+ ['Vel']
    '''
    with open(filename, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Tick']  +['Dur']  + ['Track']+ ['Chan']+['Type']+ ['Note']+ ['Vel'])
        for k in durationList:
            spamwriter.writerow(k)
            
def getSortedMessages(mid):
    ''' Calculates array of midi tupples with sorted messages by time.
    '''
    k=0
    msgList=[]
    for i, track in enumerate(mid.tracks):
        timeAcum=0
        #print('Track {}: {}'.format(i, track.name))
        for message in track:
            timeAcum = timeAcum+message.time
            #time.sleep(0.5)
            #print(k,message)
            if message.type=='note_on' or message.type=='note_off' :
                msgList.append((timeAcum,i,message.channel,message.type,message.note,message.velocity))
                k=k+1
    msgList.sort(key=lambda tup: tup[0])   
    return msgList

def calculateDurations(listaNotasOrig):
    ''' Given a sorted array of messages Calculates the duration of each Note On, by pairing with corresponding Note off
        
        Parameters
        -------------
        listNotasOrig : ArrayList of tupples
            The list of Midi notes
            
        Returns
        -------------
        listDurs : ArrayList
            New list of tupples of noteOn messages with duration
    '''
    cN=0
    dur=0
    listaNotas=listaNotasOrig[:]
    listDurs=[]
    while len(listaNotas)>0:
        if listaNotas[0][3]=='note_on':
            cN=listaNotas[0]
        for j in range(len(listaNotas)):
            if listaNotas[j][3]=='note_off' or ( listaNotas[j][3]=='note_on' and  listaNotas[j][5]==0):            
                if listaNotas[j][4] == cN[4]:
                    dur = listaNotas[j][0] - cN[0]
                    msg = (cN[0],dur, cN[1],cN[2],'note_on',cN[4],cN[5])                    
                    listDurs.append(msg)
                    del listaNotas[j]
                    del listaNotas[0]
                    break
    return listDurs
	
def printList(notesList):
    ''' Print Notes List    
    '''
    print('================================================')
    for i, m in enumerate(notesList):
        print(i,m)
        i=i+1
    print('================================================')
    