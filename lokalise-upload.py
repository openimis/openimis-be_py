# Install the Python Requests library:
# `pip install requests`
import base64
import os
import sys

import requests
import json


def send_request(filepath, tags):
    try:
        with open(filepath, "rb") as data_file:
            encoded_string = base64.b64encode(data_file.read())
    except Exception:
        print("Couldn't read file", filepath)
        raise
    try:
        response = requests.post(
            url="https://api.lokalise.com/api2/projects/539322845d9e1249837338.65707886/files/upload",
            headers={
                "Content-Type": "application/json",
                "x-api-token": api_key,
            },
            data=json.dumps({
                "data": encoded_string.decode("utf-8"),
                "filename": os.path.basename(filepath),
                "tags": tags,
                "lang_iso": "en"
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


api_key = os.environ.get("LOKALISE_APIKEY")
if not api_key:
    print("Please get your API key in your profile page and set it in the LOKALISE_APIKEY envrionment variable")
    exit()

if len(sys.argv) <= 1:
    print("Please provide as arguments the list of tags to apply to this upload. Module name and date/ticket/name.")
    exit()

send_request("django.po", sys.argv[1:])
