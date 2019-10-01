#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 15:38:24 2017

@author: holomorfo
"""
# TODO: Transform fuzzyutils to music21 


from music21 import chord,key,roman  # 5 minutos
#import pcsets as pc        # 0.3 segundos Bach prel1 epsilon 1viva import numpy as np
#import pcset_jedi as pc        # 0.3 segundos Bach prel1 epsilon 10
import csv
import numpy as np

class ChordLabels:
    segmentsList =[]
    segmentListReduced =[]
    dictAc = {"M":[0,4,7], "m":[0,3,7], "o":[0,3,6], "+":[0,4,8], "M7":[11, 0, 4, 7], "D7":[ 4,7,10, 0], "m7":[7,10,0,3 ], "o/7":[3,6,10,0], "o7":[0,3,6,9], "mM7":[11,0,3,7]}
    ''' Dictionary of chords to look for
    '''
    def __init__(self):
        print("Class created")
    
    def convertNPlist(self, list2Conv):
        retArr =[]
        if len(list2Conv)>0:    
            for elem in list2Conv:
                retArr.append(int(elem))
        return retArr
        
    def fuzzyBelonging(self,originalNotes, acordeNotas):
        ''' Calculates the fuzzy belonging function 0.0-0.1
            This function is working 
            
            Parameters:
            -----------
            originalNotes : Array of notes
                The chord we want to measure
            acordeNotas : Array of notes
                The reference Chord
            
            Returns:
            ----------
            reg : float 0.0-1.0
                The fuzzy belonging value
        '''
        reg = -1;
        intersection=list(set(originalNotes).intersection(acordeNotas))
        numerador = len(intersection)** 2;    
        #System.out.println("\nNumerador " + numerador);
        denominador = len(originalNotes)* len(acordeNotas);
        #System.out.println("Denominador " + denominador);
        if denominador != 0:
            reg = float(numerador)/ denominador;
            # System.out.println("Fuzzyness " + (reg));
    
        return reg
        
       
    def createChord(self,fund, typ):
        ''' Creates an array with the structure of the speccified chord
            This function needs to rewrite the chord to mod 12
            This function is working
            
            Parameters:
            -----------
            fund : float
                the fundamental note of the chord
            typ : string
                the type of chord according to the predefined dictionary
        '''
        typArr = np.array((np.array(self.dictAc[typ]) +fund))
            
        return typArr
    
    
    def possibleFuzzyChords(self,segmentNotes, alphaCut =0.4):
        ''' Calculates if there is an optimal fuzzy chord label for a segment of notes
        
            Parameters:
            ------------
            segmentNotes : Array of midi notes
                The segment of notes for which we are going to search for the optimal
            alphaCut : float
                Threshold fuzz value of acceptance for chords
            
            Returns:
            ------------
            possibleList
                The list of possible chords with fuzzy value abova the alpha cut
                
            Example of use:
               possibleFuzzyChords([0,3])
               
            Returns
            [(0.6666666666666666, [0, 3, 7]),
              (0.6666666666666666, [0, 3, 6]),
              (0.5, [7, 10, 0, 3]),
              (0.5, [3, 6, 10, 0]),
              (0.5, [11, 0, 3, 7])]
        '''
        tempAc = []
        tips =["M", "m", "o", "+", "M7", "D7", "m7", "o/7", "mM7"]
        fuzzyTempVal = 0;
        # I dont need a list, just the undisputable maximum.
        possibleList=[]
        # Run trough all the possible chord types
        for i in range(12):
            for j in range(len(tips)):
                # Create chord from template.. we could just have all the chords in
                # previosly defined dict created with music21
                tempAc =  self.createChord(i, tips[j])
                fuzzyTempVal = self.fuzzyBelonging(segmentNotes, tempAc)
                #print(fuzzyTempVal)
                if fuzzyTempVal > alphaCut : # alpha cut
                    possibleList.append((fuzzyTempVal,tempAc))
        possibleList.sort(key=lambda tup: tup[0],reverse=True)   
    
    
        return possibleList	
     
    
    def fuzzyOptimalUnique(self,segmentNotes, alphaCut =0.4):
        ''' Returns the maximum if exists calculated from
            possibleFuzzyChords
        '''
        ret = []
        possibleChords=self.possibleFuzzyChords(segmentNotes, alphaCut =0.4)
        if len(possibleChords)>0:
            ret = possibleChords[0]
        
        return ret        
     
    def runTroughAllSegmentsChords(self,dursList):
        ''' Run trough all segment chords and calculates the optimal fuzzy value for each of them
        
            Parameters:
            -----------
            dursList : Array midi events with durations
            
            Returns:
            ----------
            void : prints the list of optimal chords
        '''
        epsilon=10
        numNotes= len(dursList)
        posIn=0
        posFin=numNotes
        # Create segments
        for posIn in range(numNotes):
            progress = (100 * float (posIn )/ numNotes);
            print("Calculate chords ",progress)
            for posFin in range(posIn,posIn+epsilon):
                if posFin - posIn >2 and posFin < numNotes:
                    #print("-")
                    notes=[]
                    for k in range(posIn,posFin):
                        notes.append(dursList[k][5])
                    #print(notes)
                    # Label segment and add it to list
                    normList = list(chord.Chord(notes).normalOrder)   
                    optimalTup =self.fuzzyOptimalUnique(normList)
                    if len(optimalTup)>0:
                        optimalArr = self.convertNPlist( optimalTup[1])
                        #print('Optimal ',chord.Chord(optimalArr).commonName)
                        if len(optimalArr) >0:
                            c = chord.Chord(optimalArr)
                            #labelStr =c.findRoot().name+" "+c.quality
                            labelStr= c.root().name+' '+c.commonName
                            #labelArr =pc.PcSet(optimal[1]).ivec()
                            #labelStr = " ".join(str(x) for x in labelArr)
                            romanNumeral2 = roman.romanNumeralFromChord(chord.Chord(c),key.Key('c'))
                            #print('\t',romanNumeral2.romanNumeral,' in ',romanNumeral2.key.name)
                            deg = romanNumeral2.romanNumeral
                            normListStr ="-".join(str(x) for x in optimalArr)
                            notesStr = " ".join(str(x) for x in notes)
                            fuzzyVal = optimalTup[0]
                            self.segmentsList.append((posIn,posFin,normListStr,labelStr,fuzzyVal,deg,notesStr))

                                        
    def calculateSegmentsReduced(self):
        #Run trough the segment list
        self.segmentListReduced = []
        idx = 0
        segTemp =[];
        cond = True
        # break when two idx are the same
        howManySame = 0;
        idxPast = 0;
        while cond:
            print("Index non overlap ", idx)
            segTemp = self.segmentsList[idx]
            idxPast = idx;
            print('Current compare ',segTemp[5])
            for i in range(idx,len(self.segmentsList)):
                #print('\t Comparing with ',i,' ',seg)
                if not(segTemp[5] ==self.segmentsList[i][5]):
                    print('\t\tdifferent label ',self.segmentsList[i][5])
                    #If it changed, then save a segment with the current
                    # values
                    self.segmentListReduced.append((segTemp[0],self.segmentsList[i - 1][1],segTemp[2],segTemp[3],segTemp[4],segTemp[5],segTemp[6]))
                    #segmentListReduced.add(new NotesSegment(segTemp.initialNote, segmentsList.get(i - 1).finalNote,
                    #                                        segTemp.normalForm, segTemp.label, segTemp.certainty, segTemp.degree, segTemp.notas));
                    idx = i
                    break
            if idxPast == idx:
                print('how many equal')
                howManySame=howManySame+1
            if howManySame > 5 :
                print('break>5 howmanysame ',howManySame)
                break;
        return self.segmentListReduced;

    def saveCsvReducedChords(self,fileName):
        ''' Save a midi tupple as CSV
            Format ['init']  + ['final']+ ['norm_form']+['optLab']+ ['certainty']+ ['degree']+ ['notes']
        '''
        with open(fileName, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(['init']  + ['final']+ ['norm_form']+['optLab']+ ['certainty']+ ['degree']+ ['notes'])
            for k in self.segmentListReduced:
                spamwriter.writerow(k)
       
    
