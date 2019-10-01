import simplemir.fileutils as fu
import simplemir.music21utils as mu

path = 'wtcbki'

pathList = fu.get_list_files(path, extension="mid")
scores = mu.get_scores_from_paths(pathList)
print(scores[1][1])
scores[1][1].show('txt')
