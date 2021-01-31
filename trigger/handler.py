import json
import pandas as pd

from utils import *

def endpoint(event, context):
  _, payroll = read_data_from_event(event)

  payroll = payroll.rename(columns={
    "Surname": "surname",
    "First name": "name",
    "Date of birth": "birth",
    "Numéro Solde": "id_pay"
  })
  payroll['fullname'] = payroll.apply(lambda teacher: f"{teacher['surname']} _ {teacher['name']}", axis=1)
  payroll['id'] = payroll.apply(
    lambda teacher: f"{drop_digits_punctuation_and_space(teacher['surname'])} _ {drop_digits_punctuation_and_space(teacher['name'])} _ "
      f"{teacher['birth'].strftime('%d-%m-%Y')}",
    axis=1
  )

  payroll_duplicates = []
  for _, duplicate_ids in duplicate_teachers(payroll).items():
      payroll_duplicates.append([duplicate_ids[0], duplicate_ids[1:]])

  response = {
    "batch_id": event["batch_id"],
    "source_teachers": event["source_teachers"],
    "source_payrolls": event["source_payrolls"],
    "payroll_duplicates": payroll_duplicates
  }
  return response


def duplicate_teachers(payroll):
    """
    Returns a map from 'surname _ name _ birth' -> [list of the IDs (from Payroll) of the duplicated records in Payroll]
    """
    df = payroll.groupby('id')['id_pay'].apply(list).reset_index(name='ids')
    df['nb'] = df.apply(lambda teacher: len(teacher['ids']), axis=1)
    duplicates = df[df['nb'] > 1]
    duplicates_series = duplicates.set_index('id')['ids']
    return duplicates_series.to_dict()

