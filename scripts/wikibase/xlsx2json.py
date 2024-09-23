"""Test conversion from XLSX to JSON"""

import json
import sys

from openpyxl import load_workbook

PATH = "data/BDD-final2024_bon_juillet31.xlsx"
wb = load_workbook(filename = PATH)
sheet = wb['BDD final2024_bon_juillet31']

line_nb = sys.argv[1]
data = {}

data["last_name"] = sheet[f'B{line_nb}'].value
data["first_name"] = sheet[f'C{line_nb}'].value
data["full_name"] = " ".join([data["first_name"], data["last_name"]])
data["country"] = sheet[f'D{line_nb}'].value
data["gender"] = sheet[f'E{line_nb}'].value

with open("data/sample.json", "w", encoding="utf-8") as outfile: 
    json.dump(data, outfile)
