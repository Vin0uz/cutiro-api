import json
import pandas as pd
import string
import numpy as np
from collections import Counter

def damerau_levenshtein(string1, string2, t):
  '''
  Computes the Damerau-Levenshtein distance between strings. If nb of operations > t: returns 1. else: returns 0
  '''
  string1 = str(string1)
  string2 = str(string2) # convert dob

  string1 = ''.join(filter(str.isalpha, string1.lower()))
  string2 = ''.join(filter(str.isalpha, string2.lower())) # keep only letters

  if len(string1)==0:
    if string2 =='': return 0
    else: return 1

  if len(string2)==0:
    if string1 =='': return 0
    else: return 1

  d = np.zeros(shape = (len(string1), len(string2)))

  for j in range(len(string2)): d[0][j] = j

  for i in range(len(string1)): d[i][0] = i

  for i in range(len(string1)):
    for j in range(len(string2)):
      if string1[i]==string2[j]: cost = 0
      else: cost = 1
      d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + cost) # deletion, insertion or substitution

      if i > 1 and j > 1 and string1[i] == string2[j-1] and string1[i-1] == string2[j]:
        d[i][j]= min(d[i][j],d[i - 2][j - 2] + 1) # transposition

  if d[len(string1)-1][len(string2)-1] > t: return 1
  return 0

def LC_S(string1, string2, t):
  '''
  Computes a distance between strings using the longest common substring
  :return: 1 if (len(string1) + len(string2) - 2*result)/(len(string1) + len(string2)) > 1-t, 0 otherwise where result is the length of the longest common substring.
  '''

  string1 = str(string1)
  string2 = str(string2)

  string1 = ''.join(filter(str.isalpha, string1.lower()))
  string2 = ''.join(filter(str.isalpha, string2.lower())) # keep only letters

  m = len(string1)
  n = len(string2)

  if string1 in string2: return 0
  if string2 in string1: return 0


  LCSuff = [[0 for k in range(n + 1)] for l in range(m + 1)]

  # To store the length of
  # longest common substring
  result = 0

  # Following steps to build
  # LCSuff[m+1][n+1] in bottom up fashion
  for i in range(m + 1):
    for j in range(n + 1):
      if (i == 0 or j == 0):
        LCSuff[i][j] = 0
      elif (string1[i - 1] == string2[j - 1]):
        LCSuff[i][j] = LCSuff[i - 1][j - 1] + 1
        result = max(result, LCSuff[i][j])
      else:
        LCSuff[i][j] = 0
  if (len(string1) + len(string2) - 2*result)/(len(string1) + len(string2)) > 1 - t: return 1
  return 0

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
