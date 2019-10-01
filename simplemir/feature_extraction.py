from music21 import converter
from music21 import stream
from music21 import layout
from music21 import musicxml
from music21 import pitch
from music21 import note
from music21 import chord
from music21 import instrument
from music21 import interval
from music21 import tempo
from music21 import meter
from music21 import key
from music21 import roman
import numpy as np
import collections
import os


# TODO: FeatureExtraction documentation
# TODO: expand histograms to be each note a feature.
class Harmonic_Features:

    def __init__(self,dict_lists):
        list_chords_obj = dict_lists['list_chords_obj']
        list_chord_roman_obj = dict_lists['list_chord_roman_obj']
        list_chromatic_notes_obj = dict_lists['list_chromatic_notes_obj']
        list_notes_obj = dict_lists['list_notes_obj']
        list_keys = dict_lists['list_keys']
        list_diatonic_notes = dict_lists['list_diatonic_notes']
        stream_chordify =  dict_lists['stream_chordify']

        self.list_chord_str = [c.pitchedCommonName for c in list_chords_obj]
        self.list_roman_str =[d.figure for d in list_chord_roman_obj]
        self.perc_non_diatonic_notes = len(list_chromatic_notes_obj)/len(list_notes_obj)
        self.list_keys = list_keys
        self.histogram_degree_str = self.__calc_histogram_roman_str()
        self.histogram_chords_str = self.__calc_histogram_chords()
        self.perc_diatonic_notes = len(list_diatonic_notes)/len(list_notes_obj)
        self.number_key_changes = len(self.list_keys)  
        # WARNING WITH HOST CHORDS
        #self.dominant_chord  if len(self.histogram_chords_str) else 'x'
        #self.dominant_chord = self.histogram_chords_str[0]
        self.number_distinct_chords =len(self.histogram_chords_str)
        self.string_chords = self.__calc_list_chordify(stream_chordify)

    def __calc_histogram_roman_str(self):
        degreeCollect=collections.Counter(self.list_roman_str)
        histogram_degree_str =list(degreeCollect.items())
        histogram_degree_str = sorted(histogram_degree_str, key=lambda tup: tup[1],reverse=True)
        return histogram_degree_str

    def __calc_histogram_chords(self):
        degreeCollect=collections.Counter(self.list_chord_str)
        histogram_chords_str =list(degreeCollect.items())
        histogram_chords_str = sorted(histogram_chords_str, key=lambda tup: tup[1],reverse=True)
        return histogram_chords_str

    def __simpleName(self,name):
        ret = name
        if name=="major":
            ret ="M"
        elif name=="minor":
            ret ="m"
        return ret
        
    def __calc_list_chordify(self,stream_chordify):
        string_chords = ''
        for m in stream_chordify.recurse().getElementsByClass('Measure'):
            #print('measure ',m)
            for c in m.recurse().getElementsByClass('Chord'):
                #print('chord ',c.pitchedCommonName,' ofset ',c.offset,' measure ',c.measureNumber)
                #string_chords+=' '+c.normalOrderString
                qual =''
                if c.quality != 'other':
                    qual=c.quality
                    string_chords+=' '+c.root().name+''+self.__simpleName(qual)
                #c.addLyric(str(c.pitchedCommonName))
            string_chords+=' |\n'
        return string_chords

class Melodic_Features:

    def __init__(self,dict_lists,music):
        # self.music_stream = music
        list_notes_obj = dict_lists['list_notes_obj']
        list_midi = dict_lists['list_midi']
        list_rest_obj = dict_lists['list_rest_obj']
        self.number_notes = len(list_notes_obj)
        self.number_rests = len(list_rest_obj)
        self.list_notes_str = [ n.name for n in list_notes_obj]
        self.list_midi =[n.pitch.midi for n in list_notes_obj]
        self.list_pitch_classes_int =[n.pitch.midi%12 for n in list_notes_obj]
        self.range_pitch = max(list_midi)-min(list_midi)        
        self.pitch_volume = [n.volume.realized for n in list_notes_obj]
        self.histogram_notes_str = self.__calc_histogram_notes_str()
        self.histogram_pitch_class_notes = self.__calc_histogram_pitch_class()
        self.histrogram_midi = self.__calc_histogram_midi(list_midi)
        self.list_intervals_str, self.list_contours=self.__calc_list_intervals_contours(music)
        self.list_mel_changes = np.where(np.array(self.list_contours[:-1]) != np.array(self.list_contours[1:]))[0].tolist()
        self.number_mel_changes = len(self.list_mel_changes)
        self.list_intervals_int =  self.__calc_list_intervals_int(music)
        self.histrogram_mel_intervals = self.__calc_histogram_mel_intervals()
        self.pitch_class_vector = self.__calc_pitch_class_vector(list_notes_obj)
        [mn,mx,av,std]=self.__calc_stats_notes(list_midi)
        self.stats_notes_min = mn
        self.stats_notes_max = mx
        self.stats_notes_average = av 
        self.stats_notes_std = std
        [imn,imx,iav,istd] = self.__calc_stats_intervals()
        self.stats_intervals_min = imn
        self.stats_intervals_max = imx
        self.stats_intervals_average = iav
        self.stats_intervals_std = istd
        
        # TODO: Check domminant pitch calculation, it supposed to be stiring.
        # but it shows int.
        self.dominant_pitch = self.histogram_notes_str[0]
        self.dominant_pitch_class =self.histogram_pitch_class_notes[0]
        #self.__calc_proportion_interval(, interval='P1'):
        #self.__calc_number_directed_intervals(self, direction=1):


    def __calc_histogram_notes_str(self):
        notes_counter=collections.Counter(self.list_notes_str)
        notes_dict = dict(notes_counter)
        #histogram_notes_str =list(notesCollect.items())
        #histogram_notes_str = sorted(histogram_notes_str, key=lambda tup: tup[1],reverse=True)

        # Calculate general histogram
        hist_dict = dict()
        keys=["C","C#","D-","D","D#","E-","E","E#","F-","F","F#","G-","G","G#","A-","A","A#","B-","B","C-"]
        for k in keys:
            hist_dict[k]=0
        for k in notes_dict:
            hist_dict[k]=notes_dict[k]
        histogram_notes_str = [d[1] for d in hist_dict.items()]

        return histogram_notes_str

    def __calc_histogram_midi(self,list_midi):
        notesCollect=collections.Counter(list_midi)
        histrogram_midi =list(notesCollect.items())
        histrogram_midi = sorted(histrogram_midi, key=lambda tup: tup[1],reverse=True)
        return histrogram_midi

    def __calc_list_intervals_contours(self,music_stream):
        list_intervals_str=[] # CHECK
        list_contours=[]
        # Check first pitch interval
        # Check diferent instruments intervals
        lastPitch =pitch.Pitch()
        for r in music_stream.recurse():
            if type(r) is note.Note:
                #print(r.pitch)
                melInter = interval.Interval(r.pitch, lastPitch)
                direc = 0
                if melInter.direction.name == 'ASCENDING':
                    direc=1
                if melInter.direction.name == 'DESCENDING':
                    direc=-1
                list_intervals_str.append((melInter.name,direc))
                list_contours.append(direc)
            if type(r) is chord.Chord:
                #print(r.pitches[-1])
                melInter = interval.Interval(r.pitches[-1], lastPitch)
                if melInter.direction.name == 'ASCENDING':
                    direc=1
                if melInter.direction.name == 'DESCENDING':
                    direc=-1
                list_intervals_str.append((melInter.name,direc))
                list_contours.append(direc)
        return list_intervals_str,list_contours

    def __calc_list_intervals_int(self,music_stream): # CHECK
        list_intervals_int=[]
        # Check first pitch interval
        # Check diferent instruments intervals
        lastPitch =pitch.Pitch()
        for r in music_stream.recurse():
            if type(r) is note.Note:
                melInter = interval.Interval(r.pitch, lastPitch)
                list_intervals_int.append(melInter.chromatic.semitones)
            if type(r) is chord.Chord:
                melInter = interval.Interval(r.pitches[-1], lastPitch)
                list_intervals_int.append(melInter.chromatic.semitones)
        return list_intervals_int

    def __calc_histogram_mel_intervals(self): # CHECK
        list_intervalse_name_str =[ a[0] for a in self.list_intervals_str ]
        intervalsCollect=collections.Counter(list_intervalse_name_str)
        histrogram_mel_intervals =list(intervalsCollect.items())
        histrogram_mel_intervals = sorted(histrogram_mel_intervals, key=lambda tup: tup[1],reverse=True)
        return histrogram_mel_intervals

    def __calc_histogram_pitch_class(self):
        notesCollect=collections.Counter(self.list_pitch_classes_int)
        histogram_pitch_class_notes =list(notesCollect.items())
        histogram_pitch_class_notes = sorted(histogram_pitch_class_notes, key=lambda tup: tup[1],reverse=True)
        return histogram_pitch_class_notes 

    def __calc_pitch_class_vector(self, list_notes_obj):
        pitch_class_vector = [0,0,0,0,0,0,0,0,0,0,0,0]
        for h in self.histogram_pitch_class_notes:
            pitch_class_vector[h[0]]=h[1]/len(list_notes_obj)
        return pitch_class_vector

    def __calc_stats_notes(self,list_midi):
        mn = min(list_midi)
        mx = max(list_midi)
        av = int(np.average(list_midi))
        sd= int(np.std(list_midi))
        #stats_notes = ''+str(mn)+', '+str(mx)+', '+str(av)+', '+str(sd)
        #return stats_notes
        return [mn,mx,av,sd]

    def __calc_stats_intervals(self):
        mn = min(self.list_intervals_int)
        mx = max(self.list_intervals_int)
        av = int(np.average(self.list_intervals_int))
        sd= int(np.std(self.list_intervals_int))
        #stats_intervals = ''+str(mn)+', '+str(mx)+', '+str(av)+', '+str(sd)
        #return stats_intervals
        return [mn,mx,av,sd]

    def __calc_proportion_interval(self, interval='P1'):
        list_intervalse_name_str =[]
        for a in self.list_intervals_str:
            list_intervalse_name_str.append(a)
        return list_intervalse_name_str.count(interval)/len(list_intervalse_name_str)

    def __calc_number_directed_intervals(self, direction=1):
        conts =self.list_contours
        if direction == 1:
            return conts.count(1) 
        elif direction == -1:
            return conts.count(-1) 
        else:
            return 0

class Rythm_Features:

    def __init__(self,dict_lists):
        list_notes_obj = dict_lists['list_notes_obj'] 
        list_rest_obj = dict_lists['list_rest_obj']
        self.list_ioi = dict_lists['list_ioi'] 
        list_instruments = dict_lists['list_instruments'] 
        list_measures_obj = dict_lists['list_measures_obj'] 
        list_offset_notes_int = dict_lists['list_offset_notes_int'] 
        list_tempos = dict_lists['list_tempos']
        list_time_ratios_str = dict_lists['list_time_ratios_str']

        self.list_durations_notes_str =[n.duration.type for n in list_notes_obj]
        self.list_durations_rests_str =[n.duration.type for n in list_rest_obj]
        self.list_durations_str = self.list_durations_notes_str + self.list_durations_rests_str
        self.list_durations_int = [float(n.duration.quarterLength) for n in list_notes_obj]
        self.list_ioi = [float(x) for x in self.list_ioi if x != 0] # Double check
        self.list_ioi = self.__calc_list_ioi(list_offset_notes_int)    
        self.range_durations = max(self.list_durations_int)-min(self.list_durations_int)
        # TODO: Add stats of durations.
        self.number_distinct_durations = len(list(set(self.list_durations_str)))
        self.number_measures = self.__calc_number_measures(list_measures_obj,list_instruments)
        self.histogram_durations_str = self.__calc_histogram_duration_str()
        self.histogram_tempos = self.__calc_histogram_tempos(list_tempos)
        self.histogram_time_ratios = self.__calc_histogram_time_ratios(list_time_ratios_str)
        self.number_distinct_ioi = len(set(self.list_ioi))
        self.number_time_ratio_changes= len(list_time_ratios_str)
        self.number_tempo_changes = len(list_tempos)

    def __calc_number_measures(self,list_measures_obj,list_instruments):
        number_measures = int(len(list_measures_obj))
        if len(list_instruments)>0:
                number_measures = int(number_measures/len(list_instruments))
        return number_measures

    def __calc_list_ioi(self,list_offset_notes_int): # CHECK
        list_ioi=[]
        for i in range(len(list_offset_notes_int)):
            list_ioi.append(0)
            list_ioi[i]=list_offset_notes_int[i]-list_offset_notes_int[i-1]
        return list_ioi

    def __calc_histogram_duration_str(self):
        dursColection=collections.Counter(self.list_durations_str)
        histogram_durations_str =list(dursColection.items())
        histogram_durations_str = sorted(histogram_durations_str, key=lambda tup: tup[1],reverse=True)
        return histogram_durations_str

    def __calc_histogram_time_ratios(self,list_time_ratios_str):
        timeRcollections=collections.Counter(list_time_ratios_str)
        histogram_time_ratios =list(timeRcollections.items())
        histogram_time_ratios = sorted(histogram_time_ratios, key=lambda tup: tup[1],reverse=True)
        return histogram_time_ratios

    def __calc_histogram_tempos(self,list_tempos):
        tempoCollections=collections.Counter(list_tempos)
        histogram_tempos =list(tempoCollections.items())
        histogram_tempos = sorted(histogram_tempos, key=lambda tup: tup[1],reverse=True)
        return histogram_tempos

class Paradigms:

    def __init__(self,dict_lists):
        music_stream =  dict_lists['music_stream']
        self.list_paradigms_pitch, self.list_paradigms_durations, self.list_paradigms_pclass = self.__calc_paradigms(music_stream)
        self.num_paradigms_pitch = len(self.list_paradigms_pitch)
        self.num_paradigms_durations = len(self.list_paradigms_durations)
        self.num_paradigms_pclass = len(self.list_paradigms_pclass)

    def __calc_paradigms(self,music_stream):
        list_paradigms_pitch = []
        list_paradigms_durations = []
        lastTimeSignature = []
        list_paradigms_pclass = []

        c = []

        for m in music_stream.recurse().getElementsByClass('Measure'):
            durations_in_measure = []
            durmes = []
            pitches_in_measure = []
            
            for r in m.recurse():
                if not type(r) is stream.Measure and r.duration.quarterLength != 0:
                    durations_in_measure.append(float(r.duration.quarterLength))
                    durmes.append(r.duration)
                if  type(r) is chord.Chord:
                    for c in r.pitches:
                        pitches_in_measure.append(c.name)
                if  type(r) is note.Note:
                    pitches_in_measure.append(r.name)
            
            if len(durations_in_measure) < 12:
                list_paradigms_durations.append(tuple(durations_in_measure))
            
            if len(list_paradigms_pitch) < 12 and len(pitches_in_measure)>0:
                crd = chord.Chord(pitches_in_measure)
                list_paradigms_pitch.append(tuple(pitches_in_measure))
                list_paradigms_pclass.append(tuple(crd.normalOrder))

        list_paradigms_pclass=list(set(list_paradigms_pclass))
        list_paradigms_pclass.sort(key=len,reverse=False)

        list_paradigms_pitch=list(set(list_paradigms_pitch))
        list_paradigms_pitch.sort(key=len,reverse=False)
        
        list_paradigms_durations=list(set(list_paradigms_durations))
        list_paradigms_durations.sort(key=len,reverse=False)
        
        #print('Number of melody sets ', len(list_paradigms_pitch))
        #print('Number of durations sets ', len(list_paradigms_durations))
        #print('Number of pc sets ', len(list_paradigms_pclass))
        self
        return list_paradigms_pitch, list_paradigms_durations, list_paradigms_pclass

class Feature_extraction:

    def __init__(self,path,music):
        self.path = path
        self.dict_lists = dict()
        self.music_stream=music
        # Pitch
        self.dict_lists['list_notes_obj']=[]
        self.dict_lists['list_instruments'] = []
        
        # Rythm
        self.dict_lists['list_measures_obj'] = []
        self.dict_lists['list_rest_obj'] =[]
        self.dict_lists['list_offset_notes_int'] = []
        self.dict_lists['list_ioi'] = []
        self.dict_lists['list_tempos']=[]
        self.dict_lists['list_time_ratios_str']=[]

        # Harmony
        self.dict_lists['list_chords_obj'] = []
        self.dict_lists['list_chord_roman_obj'] = []
        self.dict_lists['list_diatonic_notes'] = []
        self.dict_lists['list_chromatic_notes_obj'] = []
        self.dict_lists['list_keys'] = []
        self.dict_lists['list_midi'] = []
        self.dict_lists['stream_chordify'] = self.music_stream.chordify()
        self.dict_lists['music_stream'] = self.music_stream

        # Calculate, populate lists
        self.__calculateLists()

        self.dict_lists['list_midi']  =[n.pitch.midi for n in self.dict_lists['list_notes_obj']]

        self.harmonic_features = Harmonic_Features(self.dict_lists)
        self.melodic_features = Melodic_Features(self.dict_lists,self.music_stream)
        self.rythm_features = Rythm_Features(self.dict_lists)
        self.paradigms = Paradigms(self.dict_lists)
        self.master_dict = {}
        base = os.path.basename(path)
        file_name = os.path.splitext(base)[0]
        self.master_dict["file_name"] = file_name
        self.master_dict["path"] = path

        self.master_dict['harmony']=self.harmonic_features.__dict__
        self.master_dict['melody']=self.melodic_features.__dict__
        self.master_dict['rythm']=self.rythm_features.__dict__
        self.master_dict['paradigms']=self.paradigms.__dict__
        # self.master_dict = {**self.master_dict, **self.harmonic_features.__dict__}
        # self.master_dict = {**self.master_dict, **self.melodic_features.__dict__}
        # self.master_dict = {**self.master_dict, **self.rythm_features.__dict__}
        # Paradigms work
        # self.master_dict = {**self.master_dict, **self.paradigms.__dict__}
        # self.export_dict = dict(self.master_dict)
        # del self.export_dict['music_stream']



        
    # End INIT
    #___________________________________________________________________
        
    def __calculateLists(self):
        # Check Case Partstaff
        lastOffset =0
        
        for r in self.music_stream.recurse():
            if type(r) is tempo.MetronomeMark:
                self.dict_lists['list_tempos'].append(r.number)
            if type(r) is meter.TimeSignature:
                self.dict_lists['list_time_ratios_str'].append(r.ratioString)
            if type(r) is key.KeySignature:
                self.dict_lists['list_keys'].append(r.sharps)

        for p in self.music_stream.getElementsByClass(stream.Part):
            # print(p)
            for ins in p.getElementsByClass(instrument.Instrument):
                # print('\t',ins.instrumentName)
                self.dict_lists['list_instruments'].append(ins.instrumentName)

            for m in p.getElementsByClass(stream.Measure):
                # print('\t',m)
                for r in m.recurse():
                    # TODO: Check case if no key signature
                    if type(r) is key.KeySignature:
                        # print('Key ',r)
                        current_key = r
                        currentKeyRoman = key.Key(current_key.getScale('major').tonic)
                        #currentKey.tonic = currentKey.getScale('major').tonic
                self.dict_lists['list_measures_obj'].append(m)

                for n in m.getElementsByClass(note.Note):
                    # print('\t\t',n,m.offset+n.offset)
                    if m.offset+n.offset- lastOffset<0:
                        lastOffset= m.offset

                    if self.__check_if_diatonic(n.pitch, current_key):
                        self.dict_lists['list_diatonic_notes'].append(n)
                    else:
                        self.dict_lists['list_chromatic_notes_obj'].append(n)

                    self.dict_lists['list_offset_notes_int'].append(m.offset+n.offset)
                    self.dict_lists['list_ioi'].append(m.offset+n.offset- lastOffset)
                    lastOffset = m.offset+n.offset
                    self.dict_lists['list_notes_obj'].append(n)
                
                for c in m.getElementsByClass(chord.Chord):
                    for n in c.pitches:
                        nt = note.Note(n,duration=c.duration)
                        # print('\t\tChordNote',nt,m.offset+c.offset)
                        self.dict_lists['list_notes_obj'].append(nt)

                        if self.__check_if_diatonic(n, current_key):
                            self.dict_lists['list_diatonic_notes'].append(n)
                        else:
                            self.dict_lists['list_chromatic_notes_obj'].append(n)

                    if m.offset+c.offset- lastOffset<0:
                        lastOffset= m.offset
                    self.dict_lists['list_chords_obj'].append(c)
                    rn = roman.romanNumeralFromChord(c, currentKeyRoman)
                    self.dict_lists['list_chord_roman_obj'].append(rn)
                    self.dict_lists['list_offset_notes_int'].append(m.offset+c.offset)
                    self.dict_lists['list_ioi'].append(m.offset+c.offset- lastOffset)
                    lastOffset = m.offset+c.offset
                    #print('\n')
                for r in m.getElementsByClass(note.Rest):
                    #print('\t\t',r,m.offset+r.offset)
                    self.dict_lists['list_rest_obj'].append(r)

                for v in m.getElementsByClass(stream.Voice):
                    #print('\t\t',v)
                    for n in v.getElementsByClass(note.Note):
                        #print('\t\t\t',n,m.offset+n.offset)
                        self.dict_lists['list_offset_notes_int'].append(m.offset+n.offset)
                        if m.offset+n.offset- lastOffset<0:
                            lastOffset= m.offset

                        if self.__check_if_diatonic(n.pitch, current_key):
                            self.dict_lists['list_diatonic_notes'].append(n)
                        else:
                            self.dict_lists['list_chromatic_notes_obj'].append(n)

                        self.dict_lists['list_ioi'].append(m.offset+n.offset- lastOffset)
                        lastOffset = m.offset+n.offset
                        #print('!!!!!!!!!!!!!!!',len(self.dict_lists['list_notes_obj))
                        self.dict_lists['list_notes_obj'].append(n)
                    
                    for c in v.getElementsByClass(chord.Chord):
                        for n in c.pitches:
                            nt = note.Note(n,duration=c.duration)
                            #print('\t\t\tChordNote',nt,m.offset+c.offset)
                            self.dict_lists['list_notes_obj'].append(nt)
                            if self.__check_if_diatonic(n, current_key):
                                self.dict_lists['list_diatonic_notes'].append(n)
                            else:
                                self.dict_lists['list_chromatic_notes_obj'].append(n)
                        if m.offset+c.offset- lastOffset<0:
                            lastOffset= m.offset

                        self.dict_lists['list_chords_obj'].append(c)
                        rn = roman.romanNumeralFromChord(c, currentKeyRoman)
                        self.dict_lists['list_chord_roman_obj'].append(rn)
                        self.dict_lists['list_ioi'].append(m.offset+c.offset- lastOffset)
                        lastOffset = m.offset+c.offset
                        self.dict_lists['list_offset_notes_int'].append(m.offset+c.offset)
                        #print('\n')
                    for r in v.getElementsByClass(note.Rest):
                        #print('\t\t\t',r,m.offset+r.offset)
                        self.dict_lists['list_rest_obj'].append(r)

        
    # End Calculate List
    #=========================================================

    def __check_if_diatonic(self,pitchCur, keyCur):
        ptc = keyCur.getScale('major').getPitches()
        ptc= [p.name for p in ptc]
        if pitchCur.name in ptc:
            return True
        else:
            return False

    def __call_attributes(self,fr):
        # Call variables
        # attr_list = [attr for attr in dir(fr) if not callable(getattr(fr, attr)) and not attr.startswith("_")]
        # attr_list = [attr for attr in dir(fr) if not callable(getattr(fr, attr)) ]
        attr_list = [attr for attr in dir(fr) if not callable(getattr(fr, attr)) ]
        attr_list.sort()
        for m in attr_list:
            try:
                func = getattr(fr, m)
                print('\n\t',m)
                print('\t' ,func)
            except AttributeError:
                print( m, " not found")    

    def __call_attributes_str(self,fr):
        # attr_list = [attr for attr in dir(fr) if not callable(getattr(fr, attr)) and not attr.startswith("_")]
        attr_list = [attr for attr in dir(fr) if not callable(getattr(fr, attr)) ]
        attr_list.sort()
        attrs = ""
        for attribute_name in attr_list:
            try:
                attribute_value = getattr(fr, attribute_name)
                attrs += '\n'+attribute_name+'\n'+str(attribute_value)+'\n'
                
                # if type(attribute_value) is int:
                #     attrs += '\n'+attribute_name+'\n'+str(attribute_value)+'\n'
                # if type(attribute_value) is list and len(attribute_value)>0 and type(attribute_value[0]) is int:
                #     attrs += '\n'+attribute_name+'\n'
                #     for val in attribute_value:
                #         attrs += str(val)+'\n'
                # if type(attribute_value) is tuple:
                #     attrs += '\n'+attribute_name+'\n'+str(attribute_value[0])
                
            except AttributeError:
                print(" not found")
        return attrs    

    def __call_attributes_csv_line(self,fr):
        # Call variables
        # attr_list = [attr for attr in dir(fr) if not callable(getattr(fr, attr)) and not attr.startswith("_")]
        attr_list = [attr for attr in dir(fr) if not callable(getattr(fr, attr)) ]
        attr_list.sort()
        attributes_names = ""
        attributes_values = ""
        for attribute_name in attr_list:
            try:
                attribute_value = getattr(fr, attribute_name)
                if type(attribute_value) is int:
                    attributes_names += attribute_name+','
                    attributes_values += str(attribute_value)+','
                
            except AttributeError:
                print(" not found")
        return attributes_names,attributes_values    

    def print_features(self):
        print('\n_____________________________________________')
        print('\nHarmonic features')
        self.__call_attributes(self.harmonic_features)
        print('\n_____________________________________________')
        print('Melodic features')
        self.__call_attributes(self.melodic_features)
        print('\n_____________________________________________')
        print('Rythmic features')
        self.__call_attributes(self.rythm_features)

    def out_file_features(self):
        print('\n_____________________________________________')
        output = 'nHarmonic features\n\n'
        output += self.__call_attributes_str(self.harmonic_features)
        output += '\n_________________\nMelodic features\n\n'
        output += self.__call_attributes_str(self.melodic_features)
        output += '\n_________________\nRythmic features\n\n'
        output += self.__call_attributes_str(self.rythm_features)
        return output

    def out_out_csv_line(self):
        attributes_names= '' 
        attributes_values = ''
        names, vals = self.__call_attributes_csv_line(self.harmonic_features)
        attributes_names += names 
        attributes_values += vals
        names, vals = self.__call_attributes_csv_line(self.melodic_features)
        attributes_names += names 
        attributes_values += vals
        names, vals = self.__call_attributes_csv_line(self.rythm_features)
        attributes_names += names 
        attributes_values += vals
        return "path,"+attributes_names, self.path+","+attributes_values

    #def sequenceDurationContour(self):
    #    return 0 
    #def numberDurationContourChanges(self):
    #    return 0
    #def dominantIOIR(self):
    #    return 0
    #def numberSyncopations(self):
    #    return 0
    #def dutyFactor(self):
        # Duty factor means the ratio of duration to
        # inter-onset interval.)
    #    return 0
    #def chordNamesprogression(self):
    #    return 0
    #def chordDegreeProgression(self):
    #    return 0
    #def numberAccidentalNotes(self):
    #    return 0

    # ## Timbre features

    # def instrumentPatches(self):
    #     return 0
    # 
    # def instrumentClasses(self):
    #     return 0
    # 
    # def percussionSets(self):
    #     return 0
    # 
    # def prevalentInstrument(self):
    #     return 0
    # 
    # def histogramUsedInstruments(self):
    #     return 0
    # 
    # def numberUsedInstruments(self):
    #     return 0
    # 
    # def fractionNotesUnpitchedInstruments(self):
    #     return 0
    # 
    # def fractionNotesPitchedInstruments(self):
    #     return 0
    #         
