import simplemir.fileutils as fu
import simplemir.music21utils as mu

# path = 'wtcbki'
path = 'bach/wtc'

pathList = fu.get_list_files(path, extension="musicxml")
scoreTuppleList = mu.get_scores_from_paths(pathList)
for i, e in enumerate(scoreTuppleList):
    print(i, e)

scoreTuppleList[1][1].show()
>> > ts.numerator
3
>> >
>> > ts.beatCount
