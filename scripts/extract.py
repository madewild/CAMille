"""Extracting content text from XML files"""

import os
import re
import html

DATA_PATH = "data/xml/"
files = os.listdir(DATA_PATH)

for f in files:
    lines = open(DATA_PATH+f, encoding="utf-8").readlines()
    out_path = f"data/txt/{f[:-4]}.txt"
    output = open(out_path, "w", encoding="utf-8")
    words = []
    for line in lines:
        content = re.findall(r'CONTENT="(.*?)"', line)
        if content:
            wordlist = content
            for word in wordlist:
                words.append(html.unescape(word))
    TEXT = " ".join(words)
    output.write(TEXT)
