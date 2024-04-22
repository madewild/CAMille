"""Fix edition to avoid hight numbers"""

import json
import sys
import time

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util import Retry

def requests_retry_session(
    retries=10,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 503, 504, 400),
    session=None,
):
    """Retrying upon failure"""
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

if __name__ == "__main__":

    code = sys.argv[1]
    start = int(sys.argv[2])
    try:
        end = int(sys.argv[3])
    except IndexError:
        end = start
    years = range(start, end+1)

    try:
        cred = json.load(open("credentials.json", encoding="utf-8"))
    except FileNotFoundError:
        cred = json.load(open("/var/www/camille/credentials.json", encoding="utf-8"))
    endpoint = cred["endpoint"]
    username = cred["username"]
    password = cred["password"]
    headers = {"Content-Type": "application/json; charset=utf8"}

    s = requests.Session()
    s.auth = (username, password)
    s.headers.update(headers)

    for year in years:
        es_url = f"{endpoint}/pages/_search?track_total_hits=true&q=journal:{code}%20AND%20year:{year}"
        payload = {
            "size": 10000,
            "stored_fields": []
        }
        r = requests_retry_session(session=s).post(es_url, data=json.dumps(payload), timeout=60)
        if r.status_code == 200:
            resp = json.loads(r.text)
            try:
                es_ids = set([hit["_id"] for hit in resp["hits"]["hits"]])
            except KeyError:
                print("Failing to go to next year")
                print(resp)
                sys.exit()
            nb_es_ids = len(es_ids)
            print(f"{nb_es_ids} docs found for journal {code} and year {year}")
            if nb_es_ids:
                for es_id in sorted(es_ids):
                    payload2 = {
                        "doc" : {
                            "edition": "01"
                        }
                    }
                    es_url_update = f"{endpoint}/pages/_update/{es_id}"
                    r2 = requests.request("POST", es_url_update, auth=(username, password),
                                          data=json.dumps(payload2), headers=headers, timeout=60)
                    if r2.status_code != 200:
                        print(es_id, r2.text)
                        sys.exit()
        else:
            print(f"Error {r.status_code}")
            print(r.text)
            sys.exit()
        print("Done")
        time.sleep(10)
