"""Parse XML files from S3 and retrieve text"""

import html
import json
import sys

import boto3
from bs4 import BeautifulSoup as bs
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util import Retry

def requests_retry_session(
    retries=10,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 503, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def extract_text(xml_body):
    """Extract text from XML"""
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

def write_to_es(client, bucket_name, key, cred):
    """writing payload to Elasticsearch"""
    file_name = key.split("/")[-1]
    raw_file_name = file_name[:-4]
    print(f"Processing {raw_file_name}")
    elements = raw_file_name.split("_")
    journal = elements[1]
    date = elements[2]
    docyear = date.split("-")[0]
    new_obj = client.get_object(Bucket=bucket_name, Key=key)
    body = new_obj['Body'].read()
    text = extract_text(body)
    payload = {"page": raw_file_name, "journal": journal, "year": docyear, "date": date, "text": text}
    data = json.dumps(payload)
    endpoint = cred["endpoint"]
    es_url = f"{endpoint}/pages/_doc"
    username = cred["username"]
    password = cred["password"]
    headers = {"Content-Type": "application/json; charset=utf8"}
    full_es_url = f"{es_url}/{raw_file_name}"
    s = requests.Session()
    s.auth = (username, password)
    s.headers.update(headers)
    try:
        r = requests_retry_session(session=s).put(full_es_url, data=data, timeout=5)
        if r.status_code == 201:
            print("   Done")
        elif r.status_code == 200:
            print("   Already present, skipping")
        else:
            print(f"Error {r.status_code}")
            sys.exit()
    except Exception as x:
        print(f"It failed: {x.__class__.__name__}")
        sys.exit()

if __name__ == "__main__":
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects')

    bucket_name = "camille-data"
    code = sys.argv[1]
    start = int(sys.argv[2])
    try:
        end = int(sys.argv[3])
    except IndexError:
        end = start
    years = range(start, end+1)

    try:
        credentials = json.load(open("../credentials.json"))
    except FileNotFoundError:
        credentials = json.load(open("/var/www/camille/credentials.json"))

    for year in years:
        print(f"Processing {year}...")
        prefix = f"XML/{code}/{year}"
        #prefix = f"XML/{code}/{year}/KB_{code}_{year}-1"
        
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        for page in pages:
            try:
                objects = page["Contents"]
                for obj in objects:
                    key = obj["Key"]
                    write_to_es(s3, bucket_name, key, credentials)
                    
            except KeyError:
                print(f"{year} has not been found, skipping")
