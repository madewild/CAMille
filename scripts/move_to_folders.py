"""Move files to years folders"""

import os
import shutil

path_xml = "/run/media/max/CAMille 1/JB685_XML_nomets/"
path_pdf = "/run/media/max/CAMille 1/JB685_PDF_nomets/"

xml_files = os.listdir(path_xml)
pdf_files = os.listdir(path_pdf)

for f in xml_files:
    src_path = path_xml + f
    year = f.split("_")[2].split("-")[0]
    year_path = f"{path_xml}{year}/"
    if not os.path.exists(year_path):
        os.makedirs(year_path)
    dst_path = year_path + f
    shutil.move(src_path, dst_path)

for f in pdf_files:
    src_path = path_pdf + f
    if os.path.isfile(src_path):
        year = f.split("_")[2].split("-")[0]
        year_path = f"{path_pdf}{year}/"
        if not os.path.exists(year_path):
            os.makedirs(year_path)
        dst_path = year_path + f
        shutil.move(src_path, dst_path)
