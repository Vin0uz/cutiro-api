import string
from collections import Counter

def is_anagram(str1, str2):
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))

    str1 = str1.lower().translate(translator).replace(' ', '')
    str2 = str2.lower().translate(translator).replace(' ', '')

    return Counter(str1) == Counter(str2)


def is_initials(string1, string2):
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))

    string1 = string1.lower().translate(translator).replace('  ', ' ')
    string2 = string2.lower().translate(translator).replace('  ', ' ')

    if string1 in string2: return True
    if string2 in string1: return True

    if string1 in ' ' or string2 in ' ': return True


    elem = string1.split()[0]
    if elem in string2: return is_initials(string1.split(elem, 1)[1], string2.split(elem, 1)[1])

    elem = string2.split()[0]
    if elem in string1: return is_initials(string1.split(elem, 1)[1],string2.split(elem, 1)[1])

    return False


def is_constants_dim(string1, string2):
    translator = str.maketrans('', '', 'aeiouy' + string.punctuation)

    string1 = string1.lower().translate(translator)
    string2 = string2.lower().translate(translator)


    if string1 in string2: return True
    if string2 in string1: return True

    if string1 == ' ' or string2 == ' ': return True


    elem = string1[0]
    if elem in string2 + string2.replace(' ', ''): return is_initials(string1.split(elem, 1)[1], string2.split(elem, 1)[1])

    elem = string2[0]
    if elem in string1 + string1.replace(' ', ''): return is_initials(string1.split(elem, 1)[1],string2.split(elem, 1)[1])

    return False
