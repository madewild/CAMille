"""Parse XML files from S3 and retrieve text"""

import html
import json
import sys

import boto3
from bs4 import BeautifulSoup as bs
import requests

s3 = boto3.client('s3')
s3r = boto3.resource('s3')

bucket_name = "camille-data"
start = sys.argv[1]
end = sys.argv[2]
years = range(start, end+1)

try:
    cred = json.load(open("../es_credentials.json"))
except FileNotFoundError:
    cred = json.load(open("/var/www/camille/es_credentials.json"))
endpoint = cred["endpoint"]
es_url = f"{endpoint}/pages/_doc"
username = cred["username"]
password = cred["password"]
headers = {"Content-Type": "application/json; charset=utf8"}

for year in years:
    print(f"Processing {year}...")
    prefix = f"XML/JB421/{year}"
    obj_list = s3.list_objects(Bucket=bucket_name, Prefix=prefix)
    try:
        objects = obj_list["Contents"]
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
            r = requests.post(es_url, auth=(username, password), headers=headers, data=data)
            if r.status_code != 201:
                print(r.status_code)
                sys.exit()
    except KeyError:
        print(f"{year} has not been found, skipping")
