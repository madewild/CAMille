"""Index in a new ES directly from TXT files"""

import datetime
import html
import json
import os
import sys

import urllib3

urllib3.disable_warnings()

import requests

cred = json.load(open("../credentials.json", encoding="utf-8"))
endpoint = cred["endpoint"]
url = f"{endpoint}/pages/_doc"
username = cred["username"]
password = cred["password"]
auth = (username, password)
headers = {"Content-Type": "application/json; charset=utf8"}

def write_to_es(path_with_year, txt_file):
    """Writing TXT file content and metadata to ES"""
    # Get metadata
    raw_file_name = txt_file[:-4]
    elements = raw_file_name.split("_")
    journal = elements[1]
    date = elements[2]
    if elements[0] == "BE-KBR00": # new KBR format
        if journal == "15463334": # La Presse
            journal = "B14138"
        else: # unknown journal
            sys.exit()
        edition = elements[7]
        pagenb = "0" + elements[8] # add leading zero
        date = date[:4] + "-" + date[4:6] + "-" + date[6:8]
        date_format = "%Y%m%d"
    else:
        ed_page = elements[3]
        ep_elems = ed_page.split("-")
        edition = ep_elems[0]
        pagenb = ep_elems[1]
        date_format = "%Y-%m-%d"
    date_elems = date.split("-")
    year = date_elems[0]
    month = date_elems[1]
    day = date_elems[2]
    ts = datetime.datetime.strptime(date, date_format)
    dow = str(ts.weekday() + 1)

    # Process TXT
    text = open(f"{path_with_year}/{txt_file}").read()

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
    r = requests.put(full_es_url, auth=auth, data=data, headers=headers, timeout=60, verify=False)

if __name__ == "__main__":
    
    code = sys.argv[1]
    path = f"/mnt/data/TXT/{code}"
    years = os.listdir(path)
    
    for year in sorted(years):
        print(f"Processing {year}...")
        path_with_year = f"{path}/{year}"
        txt_files = os.listdir(path_with_year)
        print(f"{len(txt_files)} files found")
        for txt_file in txt_files:
            write_to_es(path_with_year, txt_file)
