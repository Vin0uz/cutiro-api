from utils import *
import uuid


def start(event, context):
  # Collect data with no filtering based on previous matches
  emis, payroll = read_data_from_event({
      "source_teachers": event["source_teachers"],
      "source_payrolls": event["source_payrolls"]
  })

  filename = f'{uuid.uuid1()}.xlsx'
  filepath = f'/tmp/{filename}'
  output_excels(payroll, emis, event, filepath)

  file_url = save_excel_on_s3(filepath, filename)

  response = {
    "id": event["id"],
    "file_url": file_url
  }

  print(response)
  return response
