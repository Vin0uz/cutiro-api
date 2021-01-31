from tqdm import tqdm

from utils import *
from scoring import *

def start(event, context):
  emis, payroll = read_data_from_event(event)

  emis['clean_name'] = clean_data(emis['teacher_name'])
  emis['clean_surname'] = clean_data(emis['teacher_surname'])
  payroll['clean_surname'] = clean_data(payroll['Surname'])
  payroll['clean_name'] = clean_data(payroll['First name'])

  mapping, t_df_emis, t_df_payroll = low_similary_match(emis, payroll)

  response = {
    "batch_id": event["batch_id"],
    "source_teachers": event["source_teachers"],
    "source_payrolls": event["source_payrolls"],
    "step1_ids": event["step1_ids"],
    "step2_ids": event["step2_ids"],
    "step3_ids": event["step3_ids"],
    "step4_ids": json.dumps(mapping, cls=NpEncoder)
  }

  return response


def distance(string1, string2, threshold):
  a, b = threshold
  if string1 in string2 or string2 in string2: return 0
  if is_anagram(string1, string2): return 0
  if damerau_levenshtein(string1, string2, a) == 0: return 0
  if LC_S(string1, string2, b) == 0: return 0
  if is_initials(string1, string2): return 0
  if is_constants_dim(string1, string2): return 0
  return 1


def low_similary_match(emis, payroll, threshold=(2, 0.7)):
  """
  Retourne la liste des correspondances (simples et multiples) pour lesquelles on est peu surs.
  """
  t_df_emis = emis.copy()
  t_df_payroll = payroll.copy()
  res = []
  for i in tqdm(payroll.index):
    p_id = payroll._get_value(i, 'Numéro Solde')
    p_surname = payroll._get_value(i, 'clean_surname')
    p_firstname = payroll._get_value(i, 'clean_name')
    p_dob = payroll._get_value(i, 'Date of birth')

    ## same dob:
    df_dob = emis[emis['Date of birth'] == p_dob]
    for j in df_dob.index:
      e_id = df_dob._get_value(j, 'Numéro EMIS')
      e_clean_surname = df_dob._get_value(j, 'clean_surname')
      e_surname = df_dob._get_value(j, 'teacher_surname')
      e_firstname = df_dob._get_value(j, 'teacher_name')
      e_clean_firstname = df_dob._get_value(j, 'clean_name')

      if (distance(p_surname, e_surname, threshold) == 0 or distance(p_surname, e_clean_surname, threshold) == 0) and \
         (distance(p_firstname, e_firstname, threshold) == 0 or distance(p_firstname, e_clean_firstname, threshold) == 0):
          res.append([p_id, e_id])
          try:
              t_df_emis = t_df_emis.drop(index=j, inplace=False)
          except:
              pass
          try:
              t_df_payroll = t_df_payroll.drop(index=i, inplace=False)
          except:
              pass

    ## same name:
    df_name = emis[emis['clean_surname'] == p_surname]
    for j in df_name.index:
      e_id = df_name._get_value(j, 'Numéro EMIS')
      e_dob = df_dob._get_value(j, 'Date of birth')
      e_firstname = df_name._get_value(j, 'teacher_name')
      e_clean_firstname = df_name._get_value(j, 'clean_name')

      if (compare_dates(str(p_dob)[:10], str(e_dob)[:10], threshold[0]) == 0) and \
        (distance(p_firstname, e_firstname, threshold) == 0 or distance(p_firstname, e_clean_firstname, threshold) == 0):
        res.append([p_id, e_id])
        try:
          t_df_emis = t_df_emis.drop(index=j, inplace=False)
        except:
          pass
        try:
          t_df_payroll = t_df_payroll.drop(index=i, inplace=False)
        except:
          pass

  return res, t_df_emis, t_df_payroll
