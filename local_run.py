import json

from step1.handler import step_1_and_2
from step2.handler import high_similary_match
from step3.handler import low_similary_match
from trigger.handler import duplicate_teachers
from utils import read_data_from_event, drop_digits_punctuation_and_space, clean_data, NpEncoder, output_excels

if __name__ == "__main__":
    event = {
      "source_teachers": "./fixtures/Namibia_teachers_data_for_Hackathon.xlsx",
      "source_payrolls": "./fixtures/Namibia_teachers_data_for_Hackathon.xlsx",
      "batch_id": 1
    }

    # TRIGGER
    print('Trigger')
    _, payroll = read_data_from_event(event)

    payroll = payroll.rename(columns={
        "Surname": "surname",
        "First name": "name",
        "Date of birth": "birth",
        "Numéro Solde": "id_pay"
    })
    payroll['fullname'] = payroll.apply(lambda teacher: f"{teacher['surname']} _ {teacher['name']}", axis=1)
    payroll['id'] = payroll.apply(
        lambda
            teacher: f"{drop_digits_punctuation_and_space(teacher['surname'])} _ {drop_digits_punctuation_and_space(teacher['name'])} _ "
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

    ## Transition
    event = response

    ## STEP 1
    print("Step 1")
    emis, payroll = read_data_from_event(event)

    emis['clean_name'] = clean_data(emis['teacher_name'])
    emis['clean_surname'] = clean_data(emis['teacher_surname'])
    payroll['clean_surname'] = clean_data(payroll['Surname'])
    payroll['clean_name'] = clean_data(payroll['First name'])

    step1, step2 = step_1_and_2(emis, payroll)

    response = {
        "batch_id": event["batch_id"],
        "source_teachers": event["source_teachers"],
        "source_payrolls": event["source_payrolls"],
        "payroll_duplicates": event["payroll_duplicates"],
        "step1_ids": json.dumps(step1, cls=NpEncoder),
        "step2_ids": json.dumps(step2, cls=NpEncoder)
    }

    ## Transition
    event = response

    ## STEP 2
    print("Step 2")
    emis, payroll = read_data_from_event(event)

    emis['clean_name'] = clean_data(emis['teacher_name'])
    emis['clean_surname'] = clean_data(emis['teacher_surname'])
    payroll['clean_surname'] = clean_data(payroll['Surname'])
    payroll['clean_name'] = clean_data(payroll['First name'])

    mapping_90, t_df_emis, t_df_payroll = high_similary_match(emis, payroll)

    response = {
        "batch_id": event["batch_id"],
        "source_teachers": event["source_teachers"],
        "source_payrolls": event["source_payrolls"],
        "payroll_duplicates": event["payroll_duplicates"],
        "step1_ids": event["step1_ids"],
        "step2_ids": event["step2_ids"],
        "step3_ids": json.dumps(mapping_90, cls=NpEncoder)
    }

    ## Transition
    event = response

    ## STEP 3
    print("Step 3")
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
        "payroll_duplicates": event["payroll_duplicates"],
        "step1_ids": event["step1_ids"],
        "step2_ids": event["step2_ids"],
        "step3_ids": event["step3_ids"],
        "step4_ids": json.dumps(mapping, cls=NpEncoder)
    }

    ## Transition
    event = response

    ## STEP 4
    print("Step 4")
    emis, payroll = read_data_from_event(event)

    # The remaining teachers in payroll are ghosts
    ghosts = list(payroll['Numéro Solde'])

    response = {
        "batch_id": event["batch_id"],
        "source_teachers": event["source_teachers"],
        "source_payrolls": event["source_payrolls"],
        "payroll_duplicates": event["payroll_duplicates"],
        "step1_ids": event["step1_ids"],
        "step2_ids": event["step2_ids"],
        "step3_ids": event["step3_ids"],
        "step4_ids": event["step4_ids"],
        "ghosts": json.dumps(ghosts, cls=NpEncoder)
    }

    ## Transition
    event = response

    ## OUTPUT
    print('Output')
    emis, payroll = read_data_from_event({
        "source_teachers": event["source_teachers"],
        "source_payrolls": event["source_payrolls"]
    })

    print(emis)
    print(payroll)
    output_excels(payroll, emis, event, './fixtures/output.xlsx')