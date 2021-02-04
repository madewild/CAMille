"""Stream S3 objects into Elasticsearch"""

import html
import json
import sys

import boto3
from bs4 import BeautifulSoup as bs
import requests

def extract_text(xml_body):
    soup = bs(xml_body, "lxml")
    extracted_lines = []
    lines = soup.find_all("textline")
    for line in lines:
        words = []
        strings = line.find_all("string")
        for string in strings:
            subs_type = string.get("subs_type")
            if subs_type:
                if subs_type == "HypPart1":
                    word = string.get("subs_content")
                elif subs_type == "HypPart2":
                    word = None
                else:
                    print(f"Unknown SUBS_TYPE: {subs_type}")
                    sys.exit()
            else:
                word = string.get("content")
            if word:
                words.append(html.unescape(word))
        extracted_line = " ".join(words)
        extracted_lines.append(extracted_line)
    extracted_text = " ".join(extracted_lines)
    return extracted_text

cred = json.load(open("es_credentials.json"))
endpoint = cred["endpoint"]
url = f"{endpoint}/pages/_doc"
username = cred["username"]
password = cred["password"]
auth = (username, password)
headers = {"Content-Type": "application/json; charset=utf8"}

s3 = boto3.client('s3')

# Lambda execution starts here
def handler(event, context):
    for record in event['Records']:

        # Get metadata
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        file_name = key.split("/")[-1]
        raw_file_name = file_name[:-4]
        elements = raw_file_name.split("_")
        journal = elements[1]
        date = elements[2]
        year = date.split("-")[0]

        # Process XML
        obj = s3.get_object(Bucket=bucket, Key=key)
        body = obj['Body'].read()
        text = extract_text(body)

        payload = {"page": raw_file_name, "journal": journal, "year": year, "date": date, "text": text}
        data = json.dumps(payload)
        full_es_url = f"{url}/{raw_file_name}"
        r = requests.put(full_es_url, auth=auth, data=data, headers=headers)
