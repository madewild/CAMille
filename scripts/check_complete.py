"""Find incomplete texts in ES"""

import json
import sys

import requests

from parse_s3 import *

bucket_name = "camille-data"
code = sys.argv[1]
try:
    years = range(int(sys.argv[2]), 1971)
except IndexError:
    years = range(1831, 1971)

cred = json.load(open("credentials.json"))
endpoint = cred["endpoint"]
username = cred["username"]
password = cred["password"]
headers = {"Content-Type": "application/json; charset=utf8"}
payload = {
            "size": 10000,
            "_source": "language*"
}

for year in years:
    es_url = f"{endpoint}/pages/_search?track_total_hits=true&q=journal:{code}%20AND%20year:{year}"
    resp = requests.request("POST", es_url, auth=(username, password), data=json.dumps(payload), headers=headers)
    resp = json.loads(resp.text)
    hits = resp["hits"]["hits"]
    es_ids = set([hit["_id"] for hit in hits])
    nb_es_ids = len(es_ids)
    print(f"{nb_es_ids} docs found for journal {code} and year {year}")
    if nb_es_ids:
        for hit in hits:
            hitid = hit["_id"]
            try:
                lang = hit["_source"]["language"]
            except KeyError:
                print(f"Missing language field for {hitid}")
                sys.exit()
