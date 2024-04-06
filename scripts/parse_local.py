"""Parse XML files from local data and retrieve text"""

import os
import sys

from parse_s3 import extract_text

journal = sys.argv[1]

data_path = f"/run/media/max/CAMille 1/{journal}/"
dirs = os.listdir(data_path)

for dir in sorted(dirs):
    print(f"Folder {dir}")
    files = os.listdir(data_path+dir)
    for f in sorted(files):
        if f.endswith(".xml"):
            xml_string = open(data_path+dir+"/"+f, encoding="utf-8").read()
            out_path = f"/run/media/max/CAMille 1/{journal}_TXT/{dir}/"
            if not os.path.exists(out_path):
                os.makedirs(out_path)
            full_out_path = f"{out_path}{f[:-4]}.txt"
            output = open(full_out_path, "w", encoding="utf-8")
            extracted_text = extract_text(xml_string)
            output.write(extracted_text)
