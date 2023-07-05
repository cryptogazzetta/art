import re
import unicodedata

def get_number(string):
    numbers = re.findall(r'\d+', string)
    return ''.join(numbers)

def remove_unicode(string):
    clean_string = ''.join(char for char in string if unicodedata.category(char)[0] != 'C')
    return clean_string