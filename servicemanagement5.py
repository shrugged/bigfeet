import google.auth.transport.requests
from google.oauth2 import service_account
import requests
import argparse
from itertools import islice
import json
import re

CREDENTIAL_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

parser = argparse.ArgumentParser()
parser.add_argument("-k", "--key", default='/Users/gb/mastermind-246704-5b556751eeba.json')
parser.add_argument("-i", "--input", help="List of subdomains input", type=argparse.FileType('r'), required=True)
args = parser.parse_args()

def get_service_account_token():
  credentials = service_account.Credentials.from_service_account_file(
          args.key, scopes=CREDENTIAL_SCOPES)
  
  credentials.refresh(google.auth.transport.requests.Request())
  return credentials.token


def chunks(data, SIZE=10000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k:data[k] for k in islice(it, SIZE)}

TAGS = set()
for i in args.input:
  TAGS.add(i.rstrip())

def bruteforce(z):
  VALID = dict()

  test = json.dumps(z, indent=4)
  headers = {"content-type": "application/json", "authorization": "Bearer " + get_service_account_token()}
  r = requests.post("https://loasproject-pa.googleapis.com/v1/services/badopsec-gpu.appspot.com/configs", headers=headers, data=test)
  j = r.json()
  if not "details" in j['error']:
    print(r.text)
    return {}
  for field in j['error']['details'][0]['fieldViolations']:
    desc = field['description']

    r = re.findall(r'Invalid value at \'(.*)\' \((.*)\)', desc)
    if r:
      VALID[r[0][0]] = r[0][1]

  return VALID

d = dict.fromkeys(TAGS, -45234234223504294885)

a = bruteforce(d)