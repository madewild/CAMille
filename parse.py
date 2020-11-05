"""Parse XML files and retrieve formatted text"""

import os
import re
import html
from bs4 import BeautifulSoup as bs

data_path = "data/xml/"
files = os.listdir(data_path)

for f in sorted(files):
    print(f"Processing {f}")
    xml_string = open(data_path+f, encoding="utf-8").read()
    soup = bs(xml_string, "lxml")
    out_path = f"data/txt/{f[:-4]}.txt"
    output = open(out_path, "w", encoding="utf-8")
    extracted_text = ""
    lines = soup.find_all("textline")
    for line in lines:
        words = []
        strings = line.find_all("string")
        for string in strings:
            word = string.get("content")
            words.append(html.unescape(word))
        extracted_line = " ".join(words) + "\n"
        extracted_text += extracted_line
    output.write(extracted_text)
