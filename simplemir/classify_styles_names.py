
def assing_class_to_string(str_list,str_classes):
    """
    Classifies strings according to a list of word classes.

    Args:
        str_list: List of strings to classify (file paths).
        str_classes: List of classes available. Each element in the list
            should be another list with equivalent tags for the class
            example [
                ['folia','fol'],
                ['pas', passacalle]
                ]

    Returns:
        Dictionary with has the classes as keys (the first representative of each class)
            and a list of the strings of str_list that correspond to that key.
            Elements that are not classified are included in the * class.
    """
    dict_classes = dict()
    # Initialize 
    dict_classes['*']=[]
    for class_array in str_classes:
        dict_classes[class_array[0]]=[]

    for current_str in str_list:
        # Check to what key the text belongs if any
        key_assigned = __assign_class(current_str.lower(),str_classes)
        # Add the path to the coresponding key
        dict_classes[key_assigned].append(current_str.lower())
    return dict_classes


# Open file with styles predefined
def get_style_lines(file_name):
    """
    Creates a list of classes from a text file .

    Args:
        file_name: The path to the filename with the string classes
            each one should be in a new line, and if a class has multiple
            definitions, it should be separated by comma. Example:

            ducal
            villano
            hacha,haches,hach
            jacara,acaras
            espanoleta,espagnoletta,esp

    Returns:
        A list in which each element correspond to a representation of the class
            if the class has multiple representations, it is represented by
            multiple elements in an array. Example        
            [
            ['ducal'],
            ['villano'],
            ['hacha','haches','hach'],
            ['jacara','acaras'],
            ['espanoleta','espagnoletta','esp'],
            ]
    """

    with open(file_name) as f:
        styles_file = f.readlines()
    style_lines = [x.strip().split(',') for x in styles_file] 
    return style_lines


def print_sorted_dict(dictionary):
    """
    Pretty prints a dictionary.

    Args:
        dictionary: A dictionary to print
    
    Returns:
        Prints each key and in the next line
        elements associated to that key
            with indentation.
    """

    for key,value in sorted(dictionary.items()):
        print(key)
        if type(value)==list:
            for entry in value:
                print('\t',entry)
        else:
            print('\t',value)

#=================================================================
# PRIVATE FUNCTIONS
#=================================================================

def __assign_class(test_str,str_classes):
    """
    Assigns a class to a string is it contains the name of the class.

    Args:
        test_str: String to test if belongs in the class
        str_classes: List of classes to test

    Returns:
        String with the associated class, if not found, returns '*'
    """

    class_tag = ''
    for class_names in str_classes:
        if __check_if_class(test_str,class_names):
            class_tag = class_names[0]
    return class_tag if class_tag != '' else '*'

# Define function to check if a sting matches a style name
def __check_if_class(test_str,class_names):
    """
    Checks if a string contains one of thenames of the class.
     
    Args:
        test_str: String to test if belongs in the class
        class_names: List of different names of a same class

    Returns:
        True if test string contains at least one of the names for the class
        False if it doesnt contain none 
    """

    vec = [ s.lower() in test_str.lower() for s in class_names ]
    # If sum is > 0 then it was true for one of the names, so bool will return true
    return bool(sum(vec))


#==========================================================================
#==========================================================================
