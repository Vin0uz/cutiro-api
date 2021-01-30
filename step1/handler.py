import pandas as pd
import re
import string
import json
import numpy as np

from tqdm import tqdm

def start(event, context):
  source_teachers = event["source_teachers"]
  source_payrolls = event["source_payrolls"]

  emis = pd.read_excel(source_teachers, sheet_name = 'EMIS').drop(columns = ['teacher_sex'])
  payroll = pd.read_excel(source_payrolls, sheet_name = 'Payroll')

  emis = emis[:200]
  payroll = payroll[:200]

  emis['teacher_name'] = (emis['teacher_name'].apply(drop_digits)).apply(drop_punctuation)
  emis['teacher_surname'] = (emis['teacher_surname'].apply(drop_digits)).apply(drop_punctuation)
  payroll['Surname'] = (payroll['Surname'].apply(drop_digits)).apply(drop_punctuation)
  payroll['First name'] = (payroll['First name'].apply(drop_digits)).apply(drop_punctuation)

  step1, step2 = step_1_and_2(emis, payroll)

  response = {
    "source_teachers": source_teachers,
    "source_payrolls": source_payrolls,
    "step1_ids": json.dumps(step1, cls=NpEncoder),
    "step2_ids": json.dumps(step2, cls=NpEncoder)
  }

  print(response)
  return response



## Utils methods
def drop_digits(word):
  word = word.translate(str.maketrans('','','0123456789'))
  return word

def drop_punctuation(word):
  word = word.translate(str.maketrans('','',string.punctuation))
  return word.lower()

def mapping_perfect_match(emis, payroll):
  # This method returns a 1:1 matching list
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
  return res, df_emis, df_payroll


def step_1_and_2(emis, payroll):
  # Returns two lists : first one is a 1:1 matching list, second is 1:N
  mapping = mapping_perfect_match(emis, payroll)[0]

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

class NpEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, np.integer):
      return int(obj)
    elif isinstance(obj, np.floating):
      return float(obj)
    elif isinstance(obj, np.ndarray):
      return obj.tolist()
    else:
      return super(NpEncoder, self).default(obj)
