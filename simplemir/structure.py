import simplemir.music21utils as mu
import matplotlib.pyplot as plt
from io import StringIO
from music21 import stream
from music21 import chord
import simplemir.music21utils as mu
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from scipy.signal import argrelextrema
import numpy as np


# ==========================================================================
# Density analysis
# ==========================================================================


def part_density_svg_string(score_file, part_group='parts'):
    """
    Creates a svg string withthe graph of the orchestal density of the
    parts in the score.

    Args: 
        score_file: A music21.score, it should have at least one part.
        part_group: String indicating a predefined group of instruments
            or part names to be analyzed    

    Returns: 
        figdata_svg: String containing the svg graph of the orchestal density
        from the input score.

    Raises: 


    """
    dens = get_part_density_file(score_file, part_group)
    plt.figure()
    plt.plot(dens)
    buf = StringIO()
    plt.savefig(buf, format='svg')
    buf.seek(0)
    figdata_svg = buf.getvalue()  # extract string
    buf.close()

    return figdata_svg


def get_part_density_file(score_file, part_group='parts'):
    """
    Calculates a orchestral density vector from a score from the instruments 
    selected in part_group

    Args: 
        score_file: A music21.score, it should have at least one part.
        part_group: String indicating a predefined group of instruments
            or part names to be analyzed    

    Returns: 
        orchestral_density: 1 x num_measures vector with the sum of 
                active parts by measure.

    Raises: 
        ValueError if strm is not a music21 score

    """
    # if type(score_file)!= stream.Score:
    #     raise ValueError('Input not a music21 score')

    # TODO: Make part names more flexible, or create more options.
    # TODO: Handle cases when the score doesnt have parts
    if part_group == 'parts':
        part_group_names = ['Tiple 1.1', 'Tiple 1.2', 'Alto 1', 'Tenor 1', 'Tiple 2.1', 'Alto 2', 'Tenor 2', 'Bajo 2', 'Soprano 1 coro 1',
                            'Soprano 2 coro 1', 'Alto coro 1', 'Tenor coro 1', 'Soprano coro 2', 'Alto coro 2', 'Tenor coro 2', 'Bajo coro 2']
    elif part_group == 'winds':
        part_group_names = ['Flauta I', 'Flauta II', 'Clarín I', 'Clarín II']
    elif part_group == 'strings':
        part_group_names = ['Violín I',
                            'Violín II', 'Bajo', 'Acompto. General']

    part_names, parts = mu.extract_parts(score_file)

    # The index of the part with a part group name
    index_parts = []
    # Check if the the part_group_names correspond to the part_names
    for v in part_group_names:
        if v in part_names:
            index_parts.append(part_names.index(v))

    # Create matrix of active measures in parts
    parts_active_vector = [mu.calc_part_active_measures(p) for p in parts]
    # Select only the parts with idx that have part names as part group names
    selected_parts_activity_matrix = [
        parts_active_vector[idx] for idx in index_parts]
    # Get sum of active selected parts in each measure
    parts_density = mu.calc_orch_density(selected_parts_activity_matrix)
    return parts_density


def get_segments_n_voices(orchestral_density_vector, voice_nums=1):
    """
    Finds the segments of n-active voices in the orchestral density vector.

    Args: 
        orchestral_density_vector: vector of 1xm, m: numbero of measures
            with an integer in each entry indicating the number of active
            parts in that measure

        voice_nums: segments with n number of active voices, for example
            1: soloist, 2: duets, etc.

    Returns: 
        segments: Vector of tupples indicating the range of measures with
            n-voices. Example, the next vector indicates that from measures
            4 to 6, 46 to 56 and 83 to 92 we have the correct number of voices.
            [(4, 6), (46, 56), (83, 92)]

    Raises: 


    """
    segments = []
    vel = []
    start = -1
    end = -1
    for i, e in enumerate(orchestral_density_vector):
        if voice_nums == e:
            vel.append(i)
            if start == -1:
                start = i
        else:
            if start != -1:
                end = i-1
                segments.append((start, end))
                start = -1
                end = -1
    if start != -1:
        end = len(orchestral_density_vector)-1
        segments.append((start, end))
        start = -1
        end = -1
    return segments

# ==========================================================================
# DTW analysis
# ==========================================================================

# only first note of chord
def measure_to_serie(meas):
    lst =[]
    for c in meas.getElementsByClass(chord.Chord):
        lst.append((float(c.offset),c.pitches[0].midi))
    return lst

# only first note of chord
def measure_list_to_serie(measL):
    lst =[]
    firstOffset = measL[0].offset
    for m in measL.getElementsByClass(stream.Measure):
        #print(m.offset,m)
        for c in m.getElementsByClass(chord.Chord):
            lst.append((float(m.offset+c.offset-firstOffset),c.pitches[0].midi))
            c.color = '#235409'
    #print(lst)
    return lst

def graph_dtw_multiple_sizes(music, minMeas=1, maxMeas=10):
    # TODO: DTW separate in various functions
    music  = mu.remove_breaks(music)
    music_chords = music.chordify()
    music_chords= mu.remove_breaks(music_chords)
    music_measures = music_chords.getElementsByClass(stream.Measure)

    numMeasMax= len(music_measures)
    # print("Num measures ",numMeasMax)
    
    plt.figure()
    for numMeasures in range(minMeas,maxMeas):
        # print(numMeasures)
        mx = numMeasures
        if numMeasures>=numMeasMax:
            mx = numMeasMax-1
        testMeasure = measure_list_to_serie( music_measures.measures(0,numMeasures) )
        listDistances=[]
        for idx in range(len(music_measures)):
            mxId = idx+numMeasures
            if numMeasures>=numMeasMax:
                mxId = numMeasMax-1
            m =music_measures.measures(idx,mxId)
            # print(len(m))
            currentMeasure = measure_list_to_serie(m)
            distance, path = fastdtw(currentMeasure, testMeasure, dist=euclidean)
            # distance= 1
            # print(distance)
            listDistances.append(distance)
        plt.plot(np.array(listDistances),label="distance")
    plt.ylabel("Relative Cost")    
    plt.xlabel("Measure")   
    plt.suptitle("Distance calculator measures from 1 to 10")
    # plt.show()

    buf = StringIO()
    plt.savefig(buf, format='svg')
    buf.seek(0)
    figdata_svg = buf.getvalue()  # extract string
    buf.close()

    return figdata_svg
