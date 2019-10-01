from music21 import converter
import simplemir.structure as st
import simplemir.music21utils as mu
import simplemir.feature_extraction as fx
import simplemir.fileutils as fu
import simplemir.classify_styles_names as stl
import json
import os
import time
import pprint



def run_json_all(path_in, extension="musicxml"):
    # TODO: Check queries json http://www.jsoniq.org/
    start_time = time.time()

    files = fu.get_list_files(path_in, extension)
    scores_db = mu.get_scores_from_paths(files)

    # Save individual JSONs
    for i, s in enumerate(scores_db):
        print(int(100*i/len(scores_db)))
        base = os.path.basename(s[0])
        file_name = os.path.splitext(base)[0]
        features = fx.Feature_extraction(s[0], s[1])
        data = json.dumps(features.master_dict)
        fu.save_file(data, path_in+'/' + file_name+'.json')
    print(100)
    # Save master JSON
    # TODO: watch out for jsons that arent file stats.
    # Maybe save data.json in other folder
    json_master = fu.merge_jsons_list(path_in)
    json_master_out = json.dumps(json_master)
    fu.save_file(json_master_out, 'analysis/data.json')

    end = time.time()
    elapsed = end - start_time
    print("\nTIME: ", elapsed)
    print("NumFiles: ", len(scores_db))

    # Create CSV files
    # From json_master, from each file, get fowllowing
    # TODO: use CSV library instead of concatenating strings
    # https://realpython.com/python-csv/
    csv_out = ""
    files_list = json_master["list_data"]
    csv_out += "file_name,"
    csv_out += "path,"
    csv_out += "Num measures,"
    csv_out += "Num notes,"
    csv_out += "Num rests,"
    csv_out += "Num chords,"
    csv_out += "Range pitch,"
    csv_out += "Range Durations,"
    csv_out += "Paradigms pitch,"
    csv_out += "Paradigms durs,"
    csv_out += "Paradigms pclass,"
    csv_out += "Num durations,"
    csv_out += "Min note,"
    csv_out += "Max note,"
    csv_out += "Average note,"
    csv_out += "Deviation notes,"
    csv_out += "Interval min,"
    csv_out += "Interval max,"
    csv_out += "Average Interval,"
    csv_out += "Deviation intervals,"
    csv_out += "Dominant pitch,"
    csv_out += "Percentage diatonic,"
    csv_out += "Num Key Changes,"
    csv_out += "Num mel changes,"
    csv_out += "Time ratio changes,"
    csv_out += "Tempo changes,"
    csv_out += "Num ioi\n"

    for elem in files_list:
        # print(elem)
        csv_out += str(elem["file_name"])+","
        csv_out += str(elem["path"])+","
        csv_out += str(elem["rythm"]['number_measures'])+","
        csv_out += str(elem["melody"]['number_notes'])+","
        csv_out += str(elem["melody"]['number_rests'])+","
        csv_out += str(elem["harmony"]['number_distinct_chords'])+","
        csv_out += str(elem["melody"]['range_pitch'])+","
        csv_out += str(elem["rythm"]['range_durations'])+","
        csv_out += str(elem["paradigms"]['num_paradigms_pitch'])+","
        csv_out += str(elem["paradigms"]['num_paradigms_durations'])+","
        csv_out += str(elem["paradigms"]['num_paradigms_pclass'])+","
        csv_out += str(elem["rythm"]['number_distinct_durations'])+","
        csv_out += str(elem["melody"]['stats_notes_min'])+","
        csv_out += str(elem["melody"]['stats_notes_max'])+","
        csv_out += str(elem["melody"]['stats_notes_average'])+","
        csv_out += str(elem["melody"]['stats_notes_std'])+","
        csv_out += str(elem["melody"]['stats_intervals_min'])+","
        csv_out += str(elem["melody"]['stats_intervals_max'])+","
        csv_out += str(elem["melody"]['stats_intervals_average'])+","
        csv_out += str(elem["melody"]['stats_intervals_std'])+","
        csv_out += str(elem["melody"]['dominant_pitch'])+","
        csv_out += str(elem["harmony"]['perc_diatonic_notes'])+","
        csv_out += str(elem["harmony"]['number_key_changes'])+","
        csv_out += str(elem["melody"]['number_mel_changes'])+","
        csv_out += str(elem["rythm"]['number_time_ratio_changes'])+","
        csv_out += str(elem["rythm"]['number_tempo_changes'])+","
        csv_out += str(elem["rythm"]['number_distinct_ioi'])+"\n"

    fu.save_file(csv_out, 'analysis/table.csv')


def run_dtw_api(in_path):
    # Configured when called from node and files in main folder
    music = converter.parse(in_path)
    music = mu.remove_breaks(music)
    svg_out = st.graph_dtw_multiple_sizes(music, 2, 3)
    # obj = {}
    # obj["elements"]=[]
    # obj["elements"].append({"svg": svg_out})
    # return obj
    return svg_out


def run_chordify_api(in_path):
    # Configured when called fro    m node and files in main folder
    music = converter.parse(in_path)
    music = music.chordify()
    music = mu.remove_breaks(music)
    xml_test = mu.stream_xml_string(music)
    return xml_test


def run_score_api(in_path):
    music = converter.parse(in_path)
    music = mu.remove_breaks(music)
    xml_test = mu.stream_xml_string(music)
    return xml_test


def run_stats_api(in_path):
    music = converter.parse(in_path)
    feats = fx.Feature_extraction(in_path, music)
    return json.dumps(feats.master_dict)


def run_classify_names(in_path):
    files = fu.get_list_files(in_path, "musicxml")
    styles_list = stl.get_style_lines('simplemir/styles.txt')
    dictionary = stl.assing_class_to_string(files,styles_list)
    return dictionary
