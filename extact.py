import simplemir.fileutils as fu
import simplemir.music21utils as mu

path = 'wtcbki'

pathList = fu.get_list_files(path, extension="mid")
scoreTuppleList = mu.get_scores_from_paths(pathList[:2])
