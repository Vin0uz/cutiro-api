from utils import *

def start(event, context):
  emis, payroll = read_data_from_event(event)

  # The remaining teachers in payroll are ghosts
  ghosts = list(payroll['Numéro Solde'])

  response = {
    "id": event["id"],
    "source_teachers": event["source_teachers"],
    "source_payrolls": event["source_payrolls"],
    "payroll_duplicates": event["payroll_duplicates"],
    "step1_ids": event["step1_ids"],
    "step2_ids": event["step2_ids"],
    "step3_ids": event["step3_ids"],
    "step4_ids": event["step4_ids"],
    "ghosts": json.dumps(ghosts, cls=NpEncoder)
  }

  print(response)
  return response
