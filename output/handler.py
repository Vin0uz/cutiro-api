from utils import *
import uuid
import requests
from requests.auth import HTTPDigestAuth
import json

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
    "result_url": file_url
  }

  url = f"https://cutiro.herokuapp.com/cleaning/refresh/{event["batch_id"]}"
  myResponse = requests.get(url, data = response)
  if(myResponse.ok):
    print("API call was ok")
  else:
    myResponse.raise_for_status()

  return response
