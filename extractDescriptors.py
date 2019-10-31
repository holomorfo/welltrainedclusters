
import simplemir.fileutils as fu
import simplemir.music21utils as mu
from music21 import stream, note, tempo, key, meter, clef, analysis, pitch
import pprint
import copy
import time
import json
import sys
print("Path", sys.argv[1])


def getMeasuresList(scores_json):
    scores = scores_json
    allMeasures = []
    lastMetronomeMark = tempo.MetronomeMark()
    lastKeysignature = key.KeySignature()
    lastTimeSignature = meter.TimeSignature()
    lastClef = clef.Clef()
    for i, strm in enumerate(scores):
        path = strm['path']
        strmScore = strm['score']
        for p in strmScore.getElementsByClass(stream.Part):
            for m in p.getElementsByClass(stream.Measure):
                isActive = False
                for r in m.recurse():
                    if type(r) == clef.TrebleClef:
                        lastClef = r
                    if type(r) == clef.BassClef:
                        lastClef = r
                    if type(r) == note.Note:
                        isActive = True
                    if type(r) == tempo.MetronomeMark:
                        lastMetronomeMark = r
                    if type(r) == key.KeySignature:
                        lastKeysignature = r
                    if type(r) == meter.TimeSignature:
                        lastTimeSignature = r
                try:
                    m.insert(0, lastTimeSignature)
                    m.insert(0, lastMetronomeMark)
                    m.insert(0, lastKeysignature)
                    m.insert(0, lastClef)
                except:
                    True
                if isActive:
                    obj = {
                        "path": path,
                        "part": p.partName,
                        "number": m.number,
                        "measure": m
                    }
                    allMeasures.append(obj)
    return allMeasures


def numberNotes(strm):
    numNotes = 0
    for e in strm.recurse():
        if type(e) == note.Note:
            numNotes += 1
    return numNotes


def counterToPitchVector(count):
    ret = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for e in count:
        ret[int(e)] = count[e]
    return ret


def letterToKey(letter, scale=20):
    isMayor = -1*scale if letter[0].islower()else scale
    pclass = pitch.Pitch(letter).pitchClass
    ret = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ret[pclass] = isMayor
    return ret


def melIntervalsHisto(melInters):
    ret = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    if len(melInters.items()) > 0:
        for key, value in melInters.items():
            #             print(key,value)
            ret[value[0].semitones % 12] = value[1]
    return ret


def calcDescriptors(inputMeasures):
    start = time.time()
    allMeasures = copy.deepcopy(inputMeasures)
    p = analysis.discrete.Ambitus()
    melIntervs = analysis.discrete.MelodicIntervalDiversity()
    for i, m in enumerate(allMeasures):
        if i % 100 == 0:
            print(int(time.time()-start), 'sec ',
                  (100*i)//len(allMeasures), '%')

        measStrm = m['measure']
        mel = melIntervs.countMelodicIntervals(measStrm)
        pcCount = analysis.pitchAnalysis.pitchAttributeCount(
            measStrm, 'pitchClass')
        desc = {
            'numberNotes': numberNotes(measStrm),
            'key': letterToKey(measStrm.analyze('key').tonicPitchNameWithCase),
            'pcCount': counterToPitchVector(pcCount),
            'melIntervs': melIntervalsHisto(mel),
            'pitchSpan': [int(thisPitch.ps) for thisPitch in p.getPitchSpan(measStrm)],
            'pitchRanges': list(p.getPitchRanges(measStrm))
        }
        desc['master'] = [desc['numberNotes']]+desc['key']+desc['pcCount'] + \
            desc['melIntervs']+desc['pitchSpan']+desc['pitchRanges']
        m['descriptors'] = desc
        m['measure'] = 'seeOtherList'
    return allMeasures


# path = 'wtca'
# path = 'wtcb'
# path = 'wtcc'
# path = 'wtcd'
start = time.time()
path = sys.argv[1]
pathList = fu.get_list_files(path, extension="xml")
scoreTuppleList = mu.get_scores_from_paths_json(pathList)
allMeasures = getMeasuresList(scoreTuppleList)
allMeasuresDesc = calcDescriptors(allMeasures)
# pprint.pprint(allMeasuresDesc)

end = time.time()
print(end - start)

with open(path+'.json', 'w') as json_file:
    json.dump(allMeasuresDesc, json_file)
