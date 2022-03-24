import google.auth.transport.requests
from google.oauth2 import service_account
import requests
import argparse
from itertools import islice
import json
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry



parser = argparse.ArgumentParser()
parser.add_argument("-k", "--key", default='/Users/gb/mastermind-246704-5b556751eeba.json')
parser.add_argument("-u", "--url", required=True)
parser.add_argument("-x", "--method", default='POST')
parser.add_argument("-t", "--test", default='')
parser.add_argument("-s", "--scope", default='cloud-platform')
parser.add_argument("-i", "--input", help="List of subdomains input", type=argparse.FileType('r'), required=True)
args = parser.parse_args()

CREDENTIAL_SCOPES = ["https://www.googleapis.com/auth/" + args.scope]

retry_strategy = Retry(
    backoff_factor=1,
    total=6,
    status_forcelist=[429],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

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

def string_to_dict(keys, value):
    key = keys.split('.')
    if len(key) == 1:
        return {key[0]: value}
    else:
        return string_to_dict('.'.join(key[:-1]), {key[-1]: value})

def bruteforce(z):
  VALID = dict()

  test = json.dumps(z, indent=4)
  headers = {"content-type": "application/json", "authorization": "Bearer " + get_service_account_token()}
  r = http.request(args.method, args.url, headers=headers, data=test)
  j = r.json()
  if not "details" in j['error']:
    print(r.text)
    return {}
  if not "fieldViolations" in j['error']['details'][0]:
    print(r.text)
    return {}
  for field in j['error']['details'][0]['fieldViolations']:
    desc = field['description']
    #print(desc)
    r = re.findall(r'Invalid value at \'[a-zA-Z_]+.(.*)\' \((.*)\)', desc)
    if r:
      VALID[r[0][0]] = r[0][1]

  return VALID

d = dict.fromkeys(TAGS, -452342342235343404294885)

if not args.test:
  a_dict = bruteforce(d)
else:
  a_dict = bruteforce(string_to_dict(args.test, d))

for key in sorted(list(a_dict)):
  print(key, '->', a_dict[key])



