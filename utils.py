import json
import pandas as pd
import string
import numpy as np

def read_data_from_event(event):
  source_teachers = event["source_teachers"]
  source_payrolls = event["source_payrolls"]

  emis = pd.read_excel(source_teachers, sheet_name = 'EMIS').drop(columns = ['teacher_sex'])
  payroll = pd.read_excel(source_payrolls, sheet_name = 'Payroll')

  emis = emis[:200]
  payroll = payroll[:200]

  return emis, payroll

def clean_data(data):
  return data.apply(drop_digits_punctuation_and_space)

def drop_digits_punctuation_and_space(word):
  chars_to_remove = string.punctuation + '0123456789' + ' '
  word = word.translate(str.maketrans('', '', chars_to_remove))
  return word


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
