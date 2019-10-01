from music21 import converter, stream, chord, scale, key
import numpy as np

# TODO: Gaspar clean code 

def normalized(a):
    maxim = np.amax(a)
    arr =[]
    for n in a:
        arr.append(n/maxim)
    return arr

class GasparChord(object):
    """Gaspar Sanz, lab:

    Attributes
        modernName
        oldName
        fret
        chordVal
    """
    def __init__(self,modern, old, frt , chrd):
        """Initiate chord."""
        self.modernName = modern
        self.oldName = old
        self.fret = frt
        self.chordVal = chrd
        

    
class Labyrinth(object):
    """Gaspar Sanz, lab:

    Attributes:
    """

    def __init__(self):
        """Initiate chord."""
        self.s = converter.parse('ChordDictionary_list.xml')
        chordListTupple =[]

        parts = self.s.getElementsByClass(stream.Part)
        for m in parts[0].getElementsByClass(stream.Measure):
            #prin t(m)
            for c in m.getElementsByClass(chord.Chord):
                #print('\t',c.lyric)
                modernName = c.lyric.split(',')[0]
                oldName = c.lyric.split(',')[1].split(':')[0]
                fret = c.lyric.split(',')[1].split(':')[1]
                nm = str(c.root())+' '+c.quality
                chordListTupple.append((modernName,oldName,fret,c,nm))

        self.dictModern = {}
        self.dictAntiguo = {}
        self.dictChords = {}
        for c in chordListTupple:
            #print(c)
            newName = c[0]
            oldName = c[1]
            fret = int(c[2])
            chordVal = c[3]
            self.dictModern[newName]=GasparChord(newName,oldName,fret,chordVal)
            self.dictAntiguo[oldName]=GasparChord(newName,oldName,fret,chordVal)
        #print(self.dictAntiguo)


    def StringOld2Chord(self,name ):
        if name.find(':')>0:
            tip = name.split(':')[0]
            fretTable = name.split(':')[1]
            if fretTable == '':
                fretTable=0
            else:
                fretTable = int(fretTable)
            retChord = self.dictAntiguo[tip].chordVal.transpose(fretTable-self.dictAntiguo[tip].fret)
        else:
            retChord = self.dictAntiguo[name].chordVal
        return retChord

    def StringOld2StringNew(self, name):
        print('StringOld2StringNew', len(name) );
    
        if len(name)==1:
            print('StringOld2StringNew', ord(name) );
        if name == ' ' or len(name)==0:
            return ''
        else: 
            print('enter',name);
            return ''+self.StringOld2Chord(name).root().name+''+self.simple_name(self.StringOld2Chord(name).quality)

    def simple_name(self,name):
        ret = name
        if name=="major":
            ret ="M"
        elif name=="minor":
            ret ="m"
        return ret

#====================================================


class FeatureVector(object):
    """Gaspar Sanz, lab:

    Attributes
    """
    def __init__(self, tuppleNotes):
        """Initiate chord."""
        self.featureVector=[]

        for i in range(0,7):
            notesList=[]
            for j in range(0,5):
                notesList.append(0)
            self.featureVector.append(notesList)

        self.featureVectorList=[]
        for i in range(0,7*5):
            self.featureVectorList.append(0)
        
        
        #self.thisChord= chrd;
        
        # check pitch list
        self.stepList=[]
        self.accList=[]
        
        for p in tuppleNotes:
            self.stepList.append(p[0])
            if p[1] == None:
                self.accList.append("")
            else:
                self.accList.append(''+p[1])
            #print(p.step, p.accidental)

        self.coord =[]
        for n in range(len(self.stepList)):
            self.coord.append((self.step2num(self.stepList[n]),self.acc2num(self.accList[n]),tuppleNotes[n][2]))

        #print(self.coord)

        for cor in self.coord:
            #print(c)
            self.featureVector[cor[0]][cor[1]]+=cor[2]
            self.featureVectorList[cor[0]*5+cor[1]]+=cor[2]
        #print(self.featureVector)
        #print(self.featureVectorList)

    def step2num(self,name):
        ret = 0
        if name =='C':
            ret = 0
        elif name =='D':
            ret = 1
        elif name =='E':
            ret = 2
        elif name =='F':
            ret = 3
        elif name =='G':
            ret = 4
        elif name =='A':
            ret = 5
        elif name =='B':
            ret = 6
        return ret

    def acc2num(self,name):
        ret = 0;
        if name =='':
            ret = 0
        elif name =='flat':
            ret = 1
        elif name =='double-flat':
            ret = 2
        elif name =='sharp':
            ret = 3
        elif name =='double-sharp':
            ret = 4
        return ret

class ChordDictionary(object):
    
    def __init__(self):
        # Set chord dictionary
        #print('Print casa ')
        self.keys=["C","C#","D-","D","D#","E-","E","E#","F-","F","F#","G-","G","G#","A-","A","A#","B-","B","C-"]
        self.mayorKeys=[]
        self.minorKeys=[]
        self.listChords=[]
        self.streamList =[]
        self.diatonicList =[]
        self.dictionaryChords=[]
        self.featuresOptimumList=[]
        self.featuresOptimum =[]
        
        # Create scales
        for k in self.keys:
            sc1 = scale.MajorScale(k)
            notes =[str(p) for p in sc1.getPitches(k+'4', k+'5')]
            notes= notes[:len(notes)-1]
            #print(k,'major', notes)
            self.mayorKeys.append((k,notes))
        
        for k in self.keys:
            sc1 = scale.MinorScale(k)
            notes =[str(p) for p in sc1.getPitches(k+'4', k+'5')]
            notes= notes[:len(notes)-1]
            #print(k.lower(),'minor', notes)
            self.minorKeys.append((k.lower(),notes))

        # Ahora generar todos los acordes posibles
        # Ahora quiero encontrar todos los acrodes diatónicos y séptimos de una tonalidad, por ejemplo

        # create all possible chords (needs to be cleaned later the list)
        count =0
        generalListChords =[]
        for m in self.mayorKeys:
            self.listChords=[]
            self.diatonicList =m[1]
            #print(diatonicList)
            for n in range(len(self.diatonicList)):
                fund =self.diatonicList[(int)(n%7)]
                third=self.diatonicList[(int)((n+2)%7)]
                fifht=self.diatonicList[(int)((n+4)%7)]
                chrd = chord.Chord([fund,third,fifht])
                #print(chrd)
                if not (chrd.pitchedCommonName in generalListChords):
                    #print('add')
                    if chrd.quality== 'mayor' or chrd.quality== 'minor':
                        self.listChords.append(chrd)
                        generalListChords.append(chrd.pitchedCommonName)

            for n in range(len(self.diatonicList)):
                fund =self.diatonicList[(int)(n%7)]
                third=self.diatonicList[(int)((n+2)%7)]
                fifht=self.diatonicList[(int)((n+4)%7)]
                svnth=self.diatonicList[(int)((n+6)%7)]
                chrd = chord.Chord([fund,third,fifht,svnth])
                #print(chrd)
                # DO NOT ADD SEVENTHS YET GASPAR
                #if not (chrd.pitchedCommonName in generalListChords):
                    #print('add')
                    #self.listChords.append(chrd)
                    #generalListChords.append(chrd.pitchedCommonName)
            s1 = stream.Stream()
            legal = key.Key(m[0])
            #print(count,"key ",m[0]," sharps",legal.sharps)
            count +=1
            s1.append(legal)

            for l in self.listChords:
                s1.append(l)
            self.streamList.append(s1);    

        #streamList[0].show('text')

        # get feature vector duration
        for st in self.streamList:
            for c in st.getElementsByClass(chord.Chord):
                noteList =[]
                #print(c)
                for n in c:
                    #print('\t',n.name)
                    if n.pitch.accidental==None:
                        acc=''
                    else:
                        acc= n.pitch.accidental.name
                    noteList.append((n.step,acc ,c.duration.quarterLength))
                    d= FeatureVector(noteList)
                self.dictionaryChords.append((c.pitchedCommonName,d.featureVectorList))
            #print(noteList)
        #print(dictionaryChords)

        #### END OF CREAT DICT
        
    def GetFeaturesFromMeasures(self,measures):
        #print(measures.quarterLength)
        cnt =0;
        self.featuresMeasures =[]
        for m in measures:
            noteList =[]
            #print(m)
            chords = m.getElementsByClass(chord.Chord)
            #print(len(chords), len(notes))
            notesStr = stream.Stream()
            notesStr.quarterLength=m.quarterLength
            #print('measure quart')
            for c in chords:
                #print('\tchord',c.duration.quarterLength)
                for n in c:
                    #print('\t',n.name)
                    if n.pitch.accidental==None:
                        acc=''
                    else:
                        acc= n.pitch.accidental.name
                    noteList.append((n.step,acc ,c.duration.quarterLength))
            #for n in noteList:
            #    print(n)

            f= FeatureVector(noteList)
            #print('measure ',cnt, '\n',normalized(f.featureVectorList))
            self.featuresMeasures.append(normalized(f.featureVectorList))
            #print(f.featureVectorList)
            cnt+=1
        return self.featuresMeasures

    def FindOptimumLabel(self, featuresMeasures):
        #featuresMeasures[2]
        # Encontrar la mejor correlación para el compás1
        self.featuresOptimum =[]
        for m in featuresMeasures:
            currChrd =m
            maxIdx =-1
            maxValue =0
            cnt =0
            listLabels = []
            for d in self.dictionaryChords:
                cVal = np.corrcoef(currChrd ,d[1])[0][1]
                if cVal> maxValue:
                    maxValue=cVal
                    maxIdx=cnt
                    #print('\t',maxValue,maxIdx)
                listLabels.append((cVal, d))
                #print('',cnt)
                cnt+=1
            listLabels = sorted(listLabels, key=lambda tup: tup[0],reverse=True)

            #print('__________________________')
            #print(m)
            self.featuresOptimumList.append(listLabels)
            self.featuresOptimum.append((maxValue,self.dictionaryChords[maxIdx]))
            #print(maxValue,'\n',dictionaryChords[maxIdx])
        return self.featuresOptimumList

    def AssignLabel(self,optimum, sch ):
        if len(optimum)== len(sch.getElementsByClass(stream.Measure)):
            print('gaspar.ChordDictionary.AssignLabel Correct num measures')
        measr=0
        for m in sch.getElementsByClass(stream.Measure):
            #print(m)
            label =''
            if len(m.getElementsByClass(chord.Chord))>0:
                firstChrd =m.getElementsByClass(chord.Chord)[0]
                #print('\tval ',optimum[measr][0])
                listPossibles=optimum[measr]
                for poss in listPossibles[:5]:
                    nameChord = poss[1][0]
                    val =''+str(round(poss[0],10))
                    label += ''+nameChord+' '+val+'\n'
                    
                #print(featuresOptimum[cnt][0])
                firstChrd.lyric=label
            measr+=1
        #scdLabels = chd.AssignLabel(ms,measures)
        return sch


    
    
    
    
    
    
    