import pandas as pd
from tqdm import tqdm
import re
import string

emis = pd.read_excel('Namibia teachers data for Hackathon.xlsx', sheet_name = 'EMIS').drop(columns = ['teacher_sex'])
payroll = pd.read_excel('Namibia teachers data for Hackathon.xlsx', sheet_name = 'Payroll')

emis = emis[:200]
payroll = payroll[:200]


def drop_digits(word):
    word = word.translate(str.maketrans('','','0123456789'))
    return word

def drop_punctuation(word):
    word = word.translate(str.maketrans('','',string.punctuation))
    return word.lower()

emis['clean_teacher_name'] = (emis['teacher_name'].apply(drop_digits)).apply(drop_punctuation)
emis['clean_teacher_surname'] = (emis['teacher_surname'].apply(drop_digits)).apply(drop_punctuation)
payroll['clean_Surname'] = (payroll['Surname'].apply(drop_digits)).apply(drop_punctuation)
payroll['clean_First name'] = (payroll['First name'].apply(drop_digits)).apply(drop_punctuation)

def mapping_correspondance_exacte():
    df_emis = emis.copy()
    df_payroll = payroll.copy()
    res = []
    for i in tqdm(payroll.index):
        p_id = payroll._get_value(i, 'Numéro Solde')
        surname = payroll._get_value(i, 'clean_Surname')
        firstname = payroll._get_value(i, 'clean_First name')
        dob = payroll._get_value(i, 'Date of birth')
        df = emis[(emis['clean_teacher_surname'] == surname)&(emis['clean_teacher_name'] == firstname)&(emis['Date of birth'] == dob)]
        for e_id in df['Numéro EMIS'].unique():
            res.append((p_id, e_id))
            j = df[df['Numéro EMIS'] == e_id].index
            try: df_emis = df_emis.drop(index = j, inplace = False)
            except: pass
            try: df_payroll = df_payroll.drop(index = i, inplace = False)
            except: pass
    return res, df_emis, df_payroll

mapping, df_emis, df_payroll = mapping_correspondance_exacte()

def step_1_et_2():
    """
    Renvoit une liste de correspondances exactes 1:1 entre les deux fichiers, et une liste de correspondances multiples.
    """
    e_dict = {}
    p_dict = {}

    for elem in mapping:
        e, p = elem
        if e not in e_dict.keys():
            e_dict[e] = [p]
        elif p not in e_dict[e]:
            e_dict[e].append(p)

        if p not in p_dict.keys():
            p_dict[p] = [e]
        elif p not in p_dict[p]:
            p_dict[p].append(e)

    unique_mapping = []
    multiple_mapping = []
    for e in e_dict.keys():
        if len(e_dict[e]) == 1:
            p = e_dict[e][0]
            if p_dict[p] == [e]: unique_mapping.append((e, p))
        else:
            for p in e_dict[e]:
                if (e,p) not in multiple_mapping: multiple_mapping.append((e, p))
                for e_p in p_dict[p]:
                    if (e_p, p) not in multiple_mapping: multiple_mapping.append((e_p, p))


    return unique_mapping, multiple_mapping


