"""Extracting content text from XML files"""

import os
import re

data_path = "data/xml/"
files = os.listdir(data_path)

for f in files:
    lines = open(data_path+f, encoding="utf-8").readlines()
    out_path = f"data/txt/{f[:-4]}.txt"
    output = open(out_path, "w", encoding="utf-8")
    words = []
    for line in lines:
        content = re.findall(r'CONTENT="(.*?)"', line)
        if content:
            wordlist = content
            for word in wordlist:
                words.append(word)
    extracted_text = " ".join(words)
    output.write(extracted_text)
