import json

def endpoint(event, context):
  source_teachers = event["source_teachers"]
  source_payrolls = event["source_payrolls"]

  return { "source_teachers": source_teachers, "source_payrolls": source_payrolls }
