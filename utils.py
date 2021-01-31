import json
import pandas as pd
import string
import numpy as np
from scoring import is_anagram
import boto3

def read_data_from_event(event):
  source_teachers = event["source_teachers"]
  source_payrolls = event["source_payrolls"]

  emis = pd.read_excel(source_teachers, sheet_name = 'EMIS').drop(columns = ['teacher_sex'])
  payroll = pd.read_excel(source_payrolls, sheet_name = 'Payroll')
  payroll = filter_payroll_with_previous_matches(payroll, event)

  emis = emis[:200]
  payroll = payroll[:200]

  return emis, payroll


def filter_payroll_with_previous_matches(payroll, event):
  # Reset index for faster deletions
  payroll = payroll.set_index('Numéro Solde', drop=False)
  # Remove duplicates from payroll
  if 'payroll_duplicates' in event:
    # Drop matched duplicates
    for _, removed in event['payroll_duplicates']:
      payroll = payroll.drop(removed)
  # Remove matched teachers
  for i in range(1, 5):
    if f"step{i}" in event:
      # event['step{i}'] contains a map of pay_id -> emis_id => Collect all pay_ids
      pay_ids = np.array(event[f"step{i}"])[:, 0]
      payroll = payroll.drop(pay_ids)
  return payroll


def clean_data(data):
  return data.apply(drop_digits_punctuation_and_space)

def drop_digits_punctuation_and_space(word):
  chars_to_remove = string.punctuation + '0123456789' + ' '
  word = word.translate(str.maketrans('', '', chars_to_remove))
  return word

def compare_dates(string1, string2, t):
  if is_anagram(string1, string2): return 0
  count = 0
  for i in range(10):
    if string1[i]!=string2[i]: count+=1

  if count>t: return 1
  return 0

def save_excel_on_s3(source = "test.xlsx", destination = "test.xlsx"):
  s3 = boto3.resource(u's3')
  bucket = s3.Bucket(u'vinouz')
  bucket.upload_file(source, destination, ExtraArgs={'ACL':'public-read'})

  object_url = "https://vinouz.s3-eu-west-1.amazonaws.com/{0}".format(destination)
  return object_url

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


def previous_matches_df(payroll, emis, event):
  # Reset index for faster deletions
  payroll = payroll.set_index('Numéro Solde', drop=False)
  # Remove duplicates from payroll
  if 'payroll_duplicates' in event:
    # Drop matched duplicates
    for _, removed in event['payroll_duplicates']:
      payroll = payroll.drop(removed)
  # Convert matches to Series and left join them
  duplicates = pd.Series(event['payroll_duplicates'], name="Duplicats de Payroll")
  payroll = payroll.join(duplicates)
  # Matched teachers
  cols = ['Match certain', 'Matchs certains', 'Matchs confiants', 'Matchs possibles']
  for i in range(1, 5):
    if f"step{i}" in event:
      name = cols[i - 1]
      # contains a map of pay_id -> emis_id => Group by pay_id and collect the list of all matching emis_ids
      matchs_series = pd.DataFrame(event[f'step{i}'], columns=["Numéro Solde", name]).groupby('Numéro Solde')[name].apply(list)
      payroll = payroll.join(matchs_series)
  # Convert list of IDs to nice display
  for col in cols:
    payroll[col].apply(lambda l: ids_to_details(l, emis))
  # Ghosts teachers
  ghosts = pd.Series(
    ['Oui' for _ in range(len(event['ghosts']))],
    name='Professeurs fantômes',
    index=pd.Index(event['ghosts'])
  )
  payroll = payroll.join(ghosts)
  return payroll


def ids_to_details(ids, emis):
    details = []
    emis = emis.set_index('Numéro EMIS')  # For faster matching
    if pd.notnull(ids):
      for e_id in ids:
          row = emis.iloc[e_id]
          birth = "né" if row['teacher_sex'] == 'Male' else 'née'
          details.append(f"{row['teacher_name']} {row['teacher_surname']}, "
                         f"{birth} le {row['Date of birth'].strftime('%d-%m-%Y')} (EMIS ID #{e_id})")
      return ", ".join(details)
    return ""


def output_excels(payroll, emis, event, filepath):
    with pd.ExcelWriter(filepath) as writer:
        previous_matches_df(payroll, emis, event).to_excel(writer, index=False, sheet_name='Payroll')
        emis.to_excel(writer, index=False, sheet_name='EMIS')
