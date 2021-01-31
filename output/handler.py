from utils import *
import uuid


def start(event, context):
  # Collect data with no filtering based on previous matches
  emis, payroll = read_data_from_event({
      "source_teachers": event["source_teachers"],
      "source_payrolls": event["source_payrolls"]
  })

  file = output_excels(payroll, emis, event)
  filename = f'{uuid.uuid1()}.xlsx'
  # ToDo @VinOuz: store in S3 bucket and return the URL
  filepath = "store file in S3"

  response = {
    "filepath": filepath
  }

  print(response)
  return response
