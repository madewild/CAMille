"""Reindex docs in ES with extra fields"""

import json
import sys

import pandas as pd
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

    bucket_name = "camille-data"
    code = sys.argv[1]
    try:
        years = [sys.argv[2]]
    except IndexError:
        years = range(1831, 1971)

    try:
        cred = json.load(open("../credentials.json"))
    except FileNotFoundError:
        cred = json.load(open("/var/www/camille/credentials.json"))
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
            for es_id in sorted(es_ids):
                print(es_id)
                elems = es_id.split("_")
                date = elems[2]
                date_elems = date.split("-")
                month = date_elems[1]
                day = date_elems[2]
                ts = pd.Timestamp(date)
                dow = str(ts.dayofweek + 1)
                ed_page = elems[3]
                ep_elems = ed_page.split("-")
                edition = ep_elems[0]
                pagenb = ep_elems[1]
                payload = {
                    "doc" : {
                        "month": month,
                        "day": day,
                        "dow": dow,
                        "edition": edition,
                        "pagenb": pagenb,
                        "language": "fr-BE"
                    }
                }
                es_url = f"{endpoint}/pages/_update/{es_id}"
                resp = requests.request("POST", es_url, auth=(username, password), data=json.dumps(payload), headers=headers)
