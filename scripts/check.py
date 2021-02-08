"""Find missing texts in ES"""

import json
import sys

import boto3
import requests

from parse_s3 import *

s3 = boto3.client('s3')
paginator = s3.get_paginator('list_objects')

bucket_name = "camille-data"
code = sys.argv[1]
year = sys.argv[2]

cred = json.load(open("../credentials.json"))
endpoint = cred["endpoint"]
es_url = f"{endpoint}/pages/_search?track_total_hits=true&q=journal:{code}%20AND%20year:{year}"
username = cred["username"]
password = cred["password"]
headers = {"Content-Type": "application/json; charset=utf8"}

payload = {
            "size": 10000,
            "stored_fields": []
}

resp = requests.request("POST", es_url, auth=(username, password), data=json.dumps(payload), headers=headers)
resp = json.loads(resp.text)
es_ids = set([hit["_id"] for hit in resp["hits"]["hits"]])

prefix = f"XML/{code}/{year}"
pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
for page in pages:
    objects = page["Contents"]
    for obj in objects:
        key = obj["Key"]
        file_name = key.split("/")[-1]
        raw_file_name = file_name[:-4]
        if raw_file_name not in es_ids:
            print(f"{raw_file_name} is missing")
            write_to_es(s3, bucket_name, key, cred)
