import requests

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
TEXTAPIKEY = os.environ.get("text-api-token")


# r = requests.post('https://textbelt.com/otp/generate', {
#   'phone': '',
#   'userid': 'exampleTestUser@aol.com',
#   'key': TEXTAPIKEY,
# })
# print(r.json())
