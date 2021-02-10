"""Find missing texts in ES"""

import json
import os
import sys

import boto3
import requests

from parse_s3 import *

s3 = boto3.client('s3')
paginator = s3.get_paginator('list_objects')

bucket_name = "camille-data"
code = sys.argv[1]
try:
    years = [sys.argv[2]]
except IndexError:
    #years = os.listdir(f"/run/media/max/Backup plus/Belgica Press XML/{code}/")
    years = range(1885, 1971)

cred = json.load(open("../credentials.json"))
endpoint = cred["endpoint"]
username = cred["username"]
password = cred["password"]
headers = {"Content-Type": "application/json; charset=utf8"}
payload = {
            "size": 10000,
            "stored_fields": []
}

for year in years:
    es_url = f"{endpoint}/pages/_search?track_total_hits=true&q=journal:{code}%20AND%20year:{year}"
    resp = requests.request("POST", es_url, auth=(username, password), data=json.dumps(payload), headers=headers)
    resp = json.loads(resp.text)
    es_ids = set([hit["_id"] for hit in resp["hits"]["hits"]])
    nb_es_ids = len(es_ids)
    print(f"{nb_es_ids} docs found for journal {code} and year {year}")

    if nb_es_ids:
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

        resp = requests.request("POST", es_url, auth=(username, password), data=json.dumps(payload), headers=headers)
        resp = json.loads(resp.text)
        new_es_ids = set([hit["_id"] for hit in resp["hits"]["hits"]])
        nb_new_es_ids = len(new_es_ids)
        if nb_new_es_ids > nb_es_ids:
            print(f"Now {nb_new_es_ids} docs for journal {code} and year {year}")
        else:
            print("Nothing missing")