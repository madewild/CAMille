"""Move files to years folders"""

import os
import shutil

PATH_XML = "/run/media/max/CAMille 1/JB685_XML_nomets/"
PATH_PDF = "/run/media/max/CAMille 1/JB685_PDF_nomets/"

xml_files = os.listdir(PATH_XML)
pdf_files = os.listdir(PATH_PDF)

for f in xml_files:
    src_path = PATH_XML + f
    year = f.split("_")[2].split("-")[0]
    year_path = f"{PATH_XML}{year}/"
    if not os.path.exists(year_path):
        os.makedirs(year_path)
    dst_path = year_path + f
    shutil.move(src_path, dst_path)

for f in pdf_files:
    src_path = PATH_PDF + f
    if os.path.isfile(src_path):
        year = f.split("_")[2].split("-")[0]
        year_path = f"{PATH_PDF}{year}/"
        if not os.path.exists(year_path):
            os.makedirs(year_path)
        dst_path = year_path + f
        shutil.move(src_path, dst_path)
