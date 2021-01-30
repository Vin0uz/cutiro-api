from fonctions_step1_step2 import *
import numpy as np

def damerau_levenshtein(string1, string2, t):
    '''
    Computes the Damerau-Levenshtein distance between strings. If nb of operations > t: returns 1. else: returns 0
    '''
    string1 = str(string1)
    string2 = str(string2) # convert dob

    string1 = string1.replace(' ', '')
    string2 = string2.replace(' ', '')
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
    m = len(string1)
    n = len(string2)

    string1 = str(string1)
    string2 = str(string2)

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


def mapping_forte_similitude(threshold = (2, 0.7)):
    """
    Retourne la liste des correspondances (simples et multiples) pour lesquelles on est surs à 90%.
    :param threshold: La distance autorisée entre deux chaînes de caractères
    """
    t_df_emis = df_emis.copy()
    t_df_payroll = df_payroll.copy()
    res = []
    for i in tqdm(payroll.index):
        p_id = payroll._get_value(i, 'Numéro Solde')
        p_surname = payroll._get_value(i, 'Surname')
        p_firstname = payroll._get_value(i, 'First name')
        p_dob = payroll._get_value(i, 'Date of birth')
        ## compare dob:
        df_dob = emis[(emis['teacher_surname'] == p_surname) & (emis['teacher_name'] == p_firstname)]
        for j in df_dob.index:
            e_id = df_dob._get_value(j, 'Numéro EMIS')
            e_dob = df_dob._get_value(j, 'Date of birth')

            if damerau_levenshtein(p_dob, e_dob, threshold[0]) == 0:
                res.append((p_id, e_id))
                try:
                    t_df_emis = t_df_emis.drop(index=j, inplace=False)
                except:
                    pass
                try:
                    t_df_payroll = t_df_payroll.drop(index=i, inplace=False)
                except:
                    pass

        ## compare surname:
        df_dob = emis[(emis['Date of birth'] == p_dob) & (emis['teacher_name'] == p_firstname)]
        for j in df_dob.index:
            e_id = df_dob._get_value(j, 'Numéro EMIS')
            e_surname = df_dob._get_value(j, 'teacher_surname')

            if damerau_levenshtein(p_surname, e_surname, threshold[0]) == 0 or LC_S(p_surname, e_surname, threshold[1]) == 0:
                res.append((p_id, e_id))
                try:
                    t_df_emis = t_df_emis.drop(index=j, inplace=False)
                except:
                    pass
                try:
                    t_df_payroll = t_df_payroll.drop(index=i, inplace=False)
                except:
                    pass

        ## compare firstname:
        df_dob = emis[(emis['Date of birth'] == p_dob) & (emis['teacher_surname'] == p_surname)]
        for j in df_dob.index:
            e_id = df_dob._get_value(j, 'Numéro EMIS')
            e_firstname = df_dob._get_value(j, 'teacher_name')

            if damerau_levenshtein(p_firstname, e_firstname, threshold[0]) == 0 or LC_S(p_firstname, e_firstname, threshold[1]) == 0:
                res.append((p_id, e_id))
                try:
                    t_df_emis = t_df_emis.drop(index=j, inplace=False)
                except:
                    pass
                try:
                    t_df_payroll = t_df_payroll.drop(index=i, inplace=False)
                except:
                    pass

    return res, t_df_emis, t_df_payroll


mapping_90, t_df_emis, t_df_payroll = mapping_forte_similitude()