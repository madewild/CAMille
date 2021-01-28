"""Parse XML files from S3 and retrieve text"""

import html
import json
import sys

import boto3
from bs4 import BeautifulSoup as bs
import requests

s3 = boto3.client('s3')
s3r = boto3.resource('s3')
paginator = s3.get_paginator('list_objects')

bucket_name = "camille-data"
start = int(sys.argv[1])
try:
    end = int(sys.argv[2])
except IndexError:
    end = start
years = range(start, end+1)

try:
    cred = json.load(open("../es_credentials.json"))
except FileNotFoundError:
    cred = json.load(open("/var/www/camille/es_credentials.json"))
endpoint = cred["endpoint"]
es_url = f"{endpoint}/pages2/_doc"
username = cred["username"]
password = cred["password"]
headers = {"Content-Type": "application/json; charset=utf8"}

for year in years:
    print(f"Processing {year}...")
    prefix = f"XML/JB421/{year}/KB_JB421_{year}-1"
    
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    for page in pages:
        try:
            objects = page["Contents"]
            for obj in objects:
                key = obj["Key"]
                file_name = key.split("/")[-1]
                raw_file_name = file_name[:-4]
                date = raw_file_name.split("_")[2]
                print(file_name)
                xml = s3r.Object(bucket_name, key)
                body = xml.get()['Body'].read()
                soup = bs(body, "lxml")
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
                payload = {"page": raw_file_name, "date": date, "text": extracted_text}
                data = json.dumps(payload)
                full_es_url = f"{es_url}/{raw_file_name}"
                r = requests.put(full_es_url, auth=(username, password), headers=headers, data=data)
                if r.status_code == 201:
                    continue
                elif r.status_code == 200:
                    print("  Already present, skipping")
                else:
                    print(r.status_code)
                    sys.exit()
        except KeyError:
            print(f"{year} has not been found, skipping")
