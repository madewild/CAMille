"""Extracting content text from XML files"""

import os
import re

data_path = "data/xml/"
files = os.listdir(data_path)

for f in files:
    lines = open(data_path+f).readlines()
    out_path = f"data/txt/{f[:-4]}.txt"
    output = open(out_path, "w")
    words = []
    for line in lines:
        content = re.findall(r'CONTENT="(.*?)"', line)
        if content:
            word = content[0]
            words.append(word)
    extracted_text = " ".join(words)
    output.write(extracted_text)
