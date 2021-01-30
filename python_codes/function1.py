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

emis['teacher_name'] = (emis['teacher_name'].apply(drop_digits)).apply(drop_punctuation)
emis['teacher_surname'] = (emis['teacher_surname'].apply(drop_digits)).apply(drop_punctuation)
payroll['Surname'] = (payroll['Surname'].apply(drop_digits)).apply(drop_punctuation)
payroll['First name'] = (payroll['First name'].apply(drop_digits)).apply(drop_punctuation)

def mapping_for_sure():
    df_emis = emis.copy()
    df_payroll = payroll.copy()
    res = []
    for i in tqdm(payroll.index):
        p_id = payroll._get_value(i, 'Numéro Solde')
        surname = payroll._get_value(i, 'Surname')
        firstname = payroll._get_value(i, 'First name')
        dob = payroll._get_value(i, 'Date of birth')
        df = emis[(emis['teacher_surname'] == surname)&(emis['teacher_name'] == firstname)&(emis['Date of birth'] == dob)]
        for e_id in df['Numéro EMIS'].unique():
            res.append((p_id, e_id))
            j = df[df['Numéro EMIS'] == e_id].index
            try: df_emis = df_emis.drop(index = j, inplace = False)
            except: pass
            try: df_payroll = df_payroll.drop(index = i, inplace = False)
            except: pass
    return res, df_payroll, df_emis

mapping, df_payroll, df_emis = mapping_for_sure()

print(mapping)