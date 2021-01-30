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
  return data.apply(drop_digits).apply(drop_punctuation)

def drop_digits(word):
  word = word.translate(str.maketrans('','','0123456789'))
  return word

def drop_punctuation(word):
  word = word.translate(str.maketrans('','',string.punctuation))
  return word.lower()

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
