from music21 import converter
from music21 import stream
from music21 import layout
from music21 import musicxml
from music21 import note
from music21 import chord
from music21 import tempo
from music21 import key
from music21 import meter
from music21 import clef



# TODO: Implement Zipf analysis, Eduardo

# TODO: Implement Hierarchical analysis of Pablo Mendoza
def get_scores_from_paths(path_list):
    """
    Takes a list of music21 file paths and returns the music21.scores
    created from them    

    Args: 
        path_list: List of strings, each element is a file path to a 
            music21 compatible file 

    Returns: 
        scores: List of tupples where the first element of the tupple is
             the path name and the second the music21.score

    Raises: 
        music21.converter.ConverterFileException: If one of the path 
        files does not link ot a music21 compatible file

    """
    scores = []
    for counter, file_path in enumerate(path_list):
        print(100*counter//len(path_list), '%')
        print(file_path)
        
        
        scores.append(remove_breaks(converter.parse(file_path)))
    return list(zip(path_list, scores))

def get_scores_from_paths_json(path_list, verbose=False):
    """
    Takes a list of music21 file paths and returns the music21.scores
    created from them    

    Args: 
        path_list: List of strings, each element is a file path to a 
            music21 compatible file 

    Returns: 
        scores: List of tupples where the first element of the tupple is
             the path name and the second the music21.score

    Raises: 
        music21.converter.ConverterFileException: If one of the path 
        files does not link ot a music21 compatible file

    """
    scores = []
    for counter, file_path in enumerate(path_list):
        if verbose:
            print(100*counter//len(path_list), '%')
            print(file_path)
        scores.append({'path':file_path,'score':remove_breaks(converter.parse(file_path))})
    return scores

# def get_measures_from_paths_json(path_dirs_list,extension='xml', verb=False):

def getMeasuresListJson(scores,verbose=False):
    allMeasures = []
    lastMetronomeMark = tempo.MetronomeMark()
    lastKeysignature = key.KeySignature()
    lastTimeSignature = meter.TimeSignature()
    lastClef = clef.Clef()
    for i, strm in enumerate(scores):
        if verbose:
            print((100*i)//len(scores),'%')
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

def thisMeasure(measJSON,allMeasures):
    for a in allMeasures:
        if measJSON['path']==a['path'] and measJSON['part']==a['part'] and measJSON['number']==a['number']:
            a['descriptors']=measJSON['descriptors']
            return a
    return 'notFound'

def measureIsMultiVoice(measureStream):
    ret = False
    numVoices = 0
    for e in measureStream.recurse():
        if type(e)== chord.Chord:
            ret = True
        if type(e)== stream.Voice:
            numVoices+=1
    if numVoices >1:
        ret = True
    return ret

def remove_breaks(strm):
    """
    Removes all page and system breaks from a music21 stream

    Args:
        strm: A music21 stream.

    Returns:
        A copy of the stream without any page or system breaks

    Raises:
        ValueError if strm is not a music21 stream
    """

    # if type(strm) != stream.Stream:
    #     raise ValueError('Input not a music21 stream')

    for m in strm.getElementsByClass(stream.Measure):
        for l in m.getElementsByClass(layout.SystemLayout):
            l.isNew = False
            # print(l.isNew)
        for l in m.getElementsByClass(layout.PageLayout):
            l.isNew = False
            # print(l.isNew)
    for p in strm.getElementsByClass(stream.PartStaff):
        for m in p.getElementsByClass(stream.Measure):
            for l in m.getElementsByClass(layout.SystemLayout):
                l.isNew = False
                # print(l.isNew)
            for l in m.getElementsByClass(layout.PageLayout):
                l.isNew = False
                # print(l.isNew)
    return strm


def stream_xml_string(strm):
    """
    Converts a music21 stream to a xml string

    Args:
        strm: A music21 stream

    Returns:
        An string containing the xml representation of the input stream

    Raises:
        ValueError if strm is not a music21 stream
    """

    # TESIS: talk about this functions
    # if type(strm) != stream.Stream:
    #     raise ValueError('Input not a music21 stream')

    GEX = musicxml.m21ToXml.GeneralObjectExporter(strm)
    out = GEX.parse()  # out is bytes in Py3
    outStr = out.decode('utf-8')  # will be string in Py3
    return outStr.strip()


def extract_parts(strm):
    """
    Takes a music21 stream and returns a list containing each one of the
    Part of the stream

    Args: 
        strm: A music21 stream

    Returns: 
        parts: List with each Part of the input stream as element. 
        part_names: List of strings with names for each Part in the stream.

     Raises:
        ValueError if strm is not a music21 stream

    """

    # TODO: Redundant function, maybe it can be suppressed
    # if type(strm)!= stream.Stream:
    #     raise ValueError('Input not a music21 stream')

    # Extract parts
    parts = strm.getElementsByClass('Part')
    # Create array with part names
    part_names = []
    for i, p in enumerate(parts):
        # print(i,p)
        part_names.append(p.partName)
    return part_names, parts


def get_pitch_list(strm):
    """
    Calculates a list of midinotes, pitchs, duration number and duration symbol
    from a music21 stream 

    Args: 
        strm: A music21.stream

    Returns: 
        pitches_in_stream: List of pitches [C,D,E, rest, etc...]
        midi_in_stream: List of MIDI notes [60,62,81,0,...]
        dur_types:['quarter', 'eight', ...]
        dur_vals: [4.0, 2.0, 2.0, 1.0, 0.5, 0.5...]


    Raises: 


    """
    pitches_in_stream = []
    midi_in_stream = []
    dur_vals = []
    dur_types = []
    for r in strm.recurse():
        if type(r) is chord.Chord:
            for c in r.pitches:
                pitches_in_stream.append(c.name)
            dur_types.append(r.duration.type)
            dur_vals.append(float(r.duration.quarterLength))
        if type(r) is note.Note:
            pitches_in_stream.append(r.name)
            midi_in_stream.append(r.pitch.midi)
            dur_types.append(r.duration.type)
            dur_vals.append(float(r.duration.quarterLength))
        if type(r) is note.Rest:
            pitches_in_stream.append(r.name)
            dur_types.append(r.duration.type)
            midi_in_stream.append(0)
            dur_vals.append(float(r.duration.quarterLength))
    return pitches_in_stream, midi_in_stream, dur_types, dur_vals


# ==========================================================================
# Density analysis
# ==========================================================================

def calc_part_active_measures(part):
    """
    Creates a vector for each measure in the part with 0 if the measure 
    has notes or chords or 0 if it is silent:

    Args: 
        part: A music21.part.

    Returns: 
        active_measures: vector of 1 and 0 corresponding to active measures 
            in the music21.part.

    Raises: 
        Value Error id part is not a music21.part

    """
    if type(part) != stream.Part:
        raise ValueError('Input not a music21 Part')

    active_measures = []
    for m in part.getElementsByClass('Measure'):
        is_playing = False
        for n in m.recurse():
            # TODO: check if active measures looks for chords
            if type(n) == note.Note:
                is_playing = True
        active_measures.append(int(is_playing))
    return active_measures


def calc_orch_density(selected_parts_activity_matrix):
    """
    Takes a n x m matrix of active parts vector, n: number of parts
    m: number of measures, calculated from calc_part_active_measures, 
    and returns a vertical sum of the active measures.

    Args: 
        selected_parts_activity_matrix: Matrix of activity vectors by part
        each row represents a part measure activity vector, 0 if the measure 
        is silent, 1 if it has notes or chords. 

    Returns: 
        orchestral_density: 1 x m vector with the sum of 
        active parts by measure

    Raises: 


    """
    orchestral_density = []
    # Take the first part active vector as length reference
    for i in range(len(selected_parts_activity_matrix[0])):
        number_active_measures = 0
        for part_vector in selected_parts_activity_matrix:
            number_active_measures += part_vector[i]
        orchestral_density.append(number_active_measures)
    return orchestral_density


# ==========================================================================
# Lyrics analysis
# ==========================================================================

def get_lyrics_from_scoresdb(scores_db):
    """
    Creates a list of lyrics objects from a scores database list.

    Args: 
        scores_db: List of path,score tupples. Example:
            [(path1, music21.score 1),
            (path1, music21.score 2),
            (path1, music21.score 3)
            ...]    
    Returns: 
        lyrics_db: List of lyrics objects from all the files in the scores_db
            Each object has the structure:
        {
            "filename": "",
            "partname": "",
            "measure": "",
            "offset": "",
            "text": ""
        }    
    Raises: 


    """
    lyrics_db = []

    for s in scores_db:
        lyr = get_lyrics_from_score(s[0], s[1])
        lyrics_db = lyrics_db + lyr

    return lyrics_db


def get_lyrics_from_score(path, score):
    """
    Returns a list of json objects with the lyrics information of the 
    input score.

    Args: 
        path: Path the the file of the score.
        score: music21 score associated with the path.

    Returns: 
        lyrics_info_db: List of json objects with information of the lyrics
            in the score, each object contains a syllable.
        {
            "filename": "",
            "partname": "",
            "measure": "",
            "offset": "",
            "text": ""
        }

    Raises: 


    """
    lyrics_info_db = []
    curren_part = ''
    # Take a score and get all elements with lyrics
    for e in score.recurse():

        # Get the name of the curent part
        if type(e) is stream.Part:
            curren_part = e.partName

        # If note, get text value, curently doesnt check for chords
        if type(e) is note.Note:

            if len(e.lyrics) > 0:
                # TODO: Check what happens on multiple lyrics
                lir_Text = e.lyrics[0].text
                ms = e.measureNumber
                ofs = e.offset
                entry = {
                    "filename": path,
                    "partname": curren_part,
                    "measure": ms,
                    "offset": ofs,
                    "text": lir_Text
                }
                lyrics_info_db.append(entry)

    return lyrics_info_db


def check_srting_files(test_string, lyrics_db_array):
    """
    Searches the lyrics database for a test string.  It compares
        lowercase version and ignores spaces, comma, dot, semicolon.
        Returns a range of measures in which the match is contained.

    Args: 
        test_string: Word or phrase to match.    
        lyrics_db_array: Array of lyrics objects with the structure:
        {
            "filename": "",
            "partname": "",
            "measure": "",
            "offset": "",
            "text": ""
        }

    Returns: 
        list_matches: List of json objects with the match informmation
            {
                "query": test_string,
                "filename": path_name,
                "partname": part_name,
                "startmeasure": start_meas,
                "endmeasure": end_meas,
            }


    Raises: 


    """
    list_matches = []
    for i in range(len(lyrics_db_array)):
        current_phrase = ''
        j = 0
        while len(current_phrase) < len(test_string):
            # print(j,len(current_phrase),len(test_string))
            list_sylable = lyrics_db_array[(
                i+j) % len(lyrics_db_array)]['text']
            current_phrase += list_sylable
            test_string_form = test_string.replace(' ', '').replace(
                ',', '').replace(';', '').replace('.', '').lower()
            current_phrase_form = current_phrase.replace(
                ',', '').replace(';', '').replace('.', '').lower()
            #print(test_string_form, '---',current_phrase_form)
            #print(test_string_form == current_phrase_form)
            if test_string_form == current_phrase_form:
                path_name = lyrics_db_array[i]['filename']
                part_name = lyrics_db_array[i]['partname']
                start_meas = lyrics_db_array[i]['measure']
                end_meas = lyrics_db_array[i+j]['measure']
                new_entry = {
                    "query": test_string,
                    "filename": path_name,
                    "partname": part_name,
                    "startmeasure": start_meas,
                    "endmeasure": end_meas,
                }
                list_matches.append(new_entry)
            j += 1

    return list_matches


def get_stream_from_match(scores_list, match_element):
    """
    Takes a lyric search match json object and the coresponding scores list
        and returns the music21 object associated with the correspondent 
        values.

    Args: 
        scores_list: List of tupples of paths and scores
            [(path1, music21.score 1),
            (path1, music21.score 2),
            (path1, music21.score 3)
            ...]

        match_element: Json object with the match lyric information.
            {
                "query": test_string,
                "filename": path_name,
                "partname": part_name,
                "startmeasure": start_meas,
                "endmeasure": end_meas,
            }

    Returns: 
        matched_stream: Music21 stream of the coresponding measures. 
            The stream has all line and page breakes removed to facilitate
            display in multiple renders.    

    Raises: 


    """
    fl_name = match_element['filename']
    pt_name = match_element['partname']
    ms_init = match_element['startmeasure']
    ms_fin = match_element['endmeasure']
    sc_num = 0

    # Find score number in list
    for i, sl in enumerate(scores_list):
        if sl[0] == fl_name:
            sc_num = i

    # Find part number by name in score
    score_matched = scores_list[sc_num][1]

    # Part names list
    pt_names = [p.partName for p in score_matched.parts]
    pt_num = pt_names.index(pt_name)
    matched_stream = score_matched.parts[pt_num].measures(ms_init, ms_fin)
    matched_stream = remove_breaks(matched_stream)

    return matched_stream


def get_matches_scores_xml(scores_list, lyric_matches):
    """
    Returns a list of musicxml files from the lyric matches 
        of the scores database list

    Args: 
        scores_list: List of tupples of paths and scores
            [(path1, music21.score 1),
            (path1, music21.score 2),
            (path1, music21.score 3)
            ...]

        lyric_matches: List of lyrics search match objects of the form:
            {
                "query": test_string,
                "filename": path_name,
                "partname": part_name,
                "startmeasure": start_meas,
                "endmeasure": end_meas,
            }

    Returns: 
        xml_list: List of musicxml strings to be displayed    

    Raises: 


    """
    xml_list = []
    for match in lyric_matches:
        stream_test = get_stream_from_match(scores_list, match)
        xml_list.append(stream_xml_string(stream_test))
    return xml_list


def write_xml_list_to_folder(xml_list, folder="output", name=""):
    """
    Writes a series of musicxml files from a list of musicxmls

    Args: 
        xml_list: List of musicxml strings
        folder: String indicating the output folder of the files.
        name: Prefix for the files, it will be populated with number
            indices.

    Returns: 
        Void: Writes files to disk

    Raises: 

    """
    # IMPORTANT:  XML encoding of accents and other symbols
    for i, xml_str in enumerate(xml_list):
        file = open(folder+'/'+name+"_"+str(i)+'.xml', 'w')
        file.write(xml_str)
        file.close()


# ==========================================================================
# MIR
# ==========================================================================


def get_list_matches(scores, lyric_matches):
    """
    Calculates a list of representative vectors of pitch and durations
        from the list of matches.

    Args: 
        scores_list: List of tupples of paths and scores
            [(path1, music21.score 1),
            (path1, music21.score 2),
            (path1, music21.score 3)
            ...]

        lyric_matches: List of lyrics search match objects of the form:
            {
                "query": test_string,
                "filename": path_name,
                "partname": part_name,
                "startmeasure": start_meas,
                "endmeasure": end_meas,
            }

    Returns: 
        pitches_matches: List of list of letter pitches for each match. 
        midi_matches: List of list of midi values for each match.
        d_types_matches: List of list of symbolic durations for each match.
        d_vals_matches: List of list of numeric durations for each match.


    Raises: 


    """
    pitches_matches = []
    midi_matches = []
    d_types_matches = []
    d_vals_matches = []

    for i, match in enumerate(lyric_matches):
        stream_test = get_stream_from_match(scores, match)
        pitches, midis, d_types, d_vals = get_pitch_list(stream_test)
        pitches_matches.append(pitches)
        midi_matches.append(tuple(midis))
        d_types_matches.append(d_types)
        d_vals_matches.append(tuple(d_vals))

    midi_matches = list(set(midi_matches))
    midi_matches.sort(key=len, reverse=False)

    d_vals_matches = list(set(d_vals_matches))
    d_vals_matches.sort(key=len, reverse=False)

    return pitches_matches, midi_matches, d_types_matches, d_vals_matches
