"""Compare XML and PDF"""

import os

PATH_XML = "/run/media/max/CAMille 1/JB685/"
PATH_PDF = "/run/media/max/CAMille 1/JB685_PDF/"

xmls = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(PATH_XML)) for f in fn]
xml_files = sorted([f.split("/")[-1][:-4] for f in xmls])
pdfs = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(PATH_PDF)) for f in fn]
pdf_files = sorted([f.split("/")[-1][:-4] for f in pdfs])

output = open("data/missing_pdf.txt", "w", encoding="utf-8")
for f in xml_files:
    if f.endswith("-mets"):
        fbis = f[:-5]
    if f not in pdf_files and fbis not in pdf_files:
        output.write(f + "\n")

output2 = open("data/missing_xml.txt", "w", encoding="utf-8")
for f in pdf_files:
    if len(f) == 22:
        fbis = f + "-mets"
    if f not in xml_files and fbis not in xml_files:
        output2.write(f + "\n")
