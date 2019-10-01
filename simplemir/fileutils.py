import os
import json


def get_list_files(root_dir, extension=""):
    """
    Finds files in subdirectories.

    Returns all files in directories and subdirectories
    from specified path.

    Args:
        root_dir: String with the parent directory to scan
        extension: extension of the files to find, for example txt, midi.
            if empty, it will return every file.

    Returns:
        A list of strings with the paths to each file found.

    Raises:

    """
    path_list = []
    for sub_dir, dirs, files in os.walk(root_dir):
        for file in files:
            if extension != "":
                curr_ext = file.split('.')[len(file.split('.'))-1]
                if curr_ext == extension:
                    path_list.append(os.path.join(sub_dir, file))
            else:
                path_list.append(os.path.join(sub_dir, file))
    return path_list


def change_extension(file_name, new_extension):
    """
    Changes the extension of a filename.

    Returns a string with the extension changed.

    Args:
        file_name: String with the name and extension of a file
        new_extension: String with the extension to chenge to
            example: txt, csv, midi.
    Returns:
        String with the same filename but with the extension replaced

    Raises:

    """
    return os.path.splitext(file_name)[0]+'.'+new_extension


def merge_jsons_list(path_in):
    list_jsons = get_list_files(path_in, "json")
    database = {}
    database['list_files'] = []
    list_data = []
    for file in list_jsons:
        with open(file) as json_file:
            data = json.load(json_file)
            list_data.append(data)
            #  print(data)
    return {"list_data": list_data}


def save_file(data, filename="test.txt"):
    file = open(filename, 'w')
    file.write(data)
    file.close()
