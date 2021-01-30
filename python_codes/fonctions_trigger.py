import pandas as pd
import string


def clean(word):
    word = word.translate(str.maketrans('', '', '0123456789'))
    word = word.translate(str.maketrans('', '', string.punctuation))
    word = word.translate(str.maketrans('', '', "-' ’"))
    return word.lower()


def collect_payroll():
    payroll = pd.read_excel('fixtures/Namibia_teachers_data_for_Hackathon.xlsx', sheet_name = 'Payroll')
    payroll = payroll[:200]
    payroll = payroll.rename(columns={
        "Surname": "surname",
        "First name": "name",
        "Date of birth": "birth",
        "Numéro Solde": "id_pay"
    })
    payroll['fullname'] = payroll.apply(lambda teacher: f"{teacher['surname']} _ {teacher['name']}", axis=1)
    payroll['id'] = payroll.apply(
        lambda teacher: f"{clean(teacher['surname'])} _ {clean(teacher['name'])} _ "
                        f"{teacher['birth'].strftime('%d-%m-%Y')}",
        axis=1
    )
    return payroll


def duplicate_teachers(payroll):
    """
    Returns a map from 'surname _ name _ birth' -> [list of the IDs (from Payroll) of the duplicated records in Payroll]
    """
    df = payroll.groupby('id')['id_pay'].apply(list).reset_index(name='ids')
    df['nb'] = df.apply(lambda teacher: len(teacher['ids']), axis=1)
    duplicates = df[df['nb'] > 1]
    duplicates_series = duplicates.set_index('id')['ids']
    return duplicates_series.to_dict()


def trigger():
    """
    Keeps only one record for the duplicated teacher in payroll
    Returns the map for each duplicate group of id -> [ids of duplicated] for the remaining teacher
    """
    payroll = collect_payroll()
    duplicates_table = {}
    for _, duplicate_ids in duplicate_teachers(payroll):
        duplicates_table[duplicate_ids[0]] = duplicate_ids[1:]
    return duplicates_table
