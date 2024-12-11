"""Test conversion from XLSX to JSON"""

import json
import sys

import pandas as pd

PATH = "data/BDD-final2024_bon_juillet31.xlsx"
df = pd.read_excel(PATH)

limit = int(sys.argv[1])
datalist = []

for line_nb in range(limit):
    data = {}
    data["last_name"] = df.iloc[line_nb, 1]
    data["first_name"] = df.iloc[line_nb, 2]
    data["full_name"] = " ".join([data["first_name"], data["last_name"]])
    data["country"] = df.iloc[line_nb, 3]
    data["gender"] = df.iloc[line_nb, 4]
    if data not in datalist:
        datalist.append(data)

with open("data/sample.json", "w", encoding="utf-8") as outfile: 
    json.dump(datalist, outfile, ensure_ascii=False)
