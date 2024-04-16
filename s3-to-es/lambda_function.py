"""Stream S3 objects into Elasticsearch"""

import datetime
import html
import json
import sys

import boto3
from bs4 import BeautifulSoup as bs
import requests

def extract_text(xml_body):
    """Extract text from XML, word by word, and join"""
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

cred = json.load(open("es_credentials.json", encoding="utf-8"))
endpoint = cred["endpoint"]
url = f"{endpoint}/pages/_doc"
username = cred["username"]
password = cred["password"]
auth = (username, password)
headers = {"Content-Type": "application/json; charset=utf8"}

s3 = boto3.client('s3')

# Lambda execution starts here
def lambda_handler(event, _):
    """Retrieving metadata"""
    for record in event['Records']:

        # Get metadata
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        file_name = key.split("/")[-1]
        raw_file_name = file_name[:-4]
        elements = raw_file_name.split("_")
        journal = elements[1]
        date = elements[2]
        if elements[0] == "BE-KBR00": # new KBR format
            if journal == "15463334": # La Presse
                journal = "B14138"
            else: # unknown journal
                sys.exit()
            year = date[:4]
            month = date[4:6]
            day = date[6:8]
            edition = elements[3]
            pagenb = "0" + elements[8] # add leading zero
            date_format = "%Y%m%d"
        else:
            date_elems = date.split("-")
            year = date_elems[0]
            month = date_elems[1]
            day = date_elems[2]
            ed_page = elements[3]
            ep_elems = ed_page.split("-")
            edition = ep_elems[0]
            pagenb = ep_elems[1]
            date_format = "%Y-%m-%d"
        ts = datetime.datetime.strptime(date, date_format)
        dow = str(ts.weekday() + 1)

        # Process XML
        obj = s3.get_object(Bucket=bucket, Key=key)
        body = obj['Body'].read()
        text = extract_text(body)

        payload = {
            "page": raw_file_name, 
            "journal": journal,
            "date": date,
            "year": year, 
            "month": month,
            "day": day,
            "dow": dow,
            "edition": edition,
            "pagenb": pagenb,
            "language": "fr-BE",
            "text": text
        }
        data = json.dumps(payload)
        full_es_url = f"{url}/{raw_file_name}"
        _ = requests.put(full_es_url, auth=auth, data=data, headers=headers, timeout=60)
