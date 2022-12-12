"""Compare XML and PDF"""

import os

path_xml = "/run/media/max/CAMille 1/JB685/"
path_pdf = "/run/media/max/CAMille 1/JB685_PDF/"

xml_files = sorted([f.split("/")[-1][:-4] for f in [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(path_xml)) for f in fn]])
pdf_files = sorted([f.split("/")[-1][:-4] for f in [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(path_pdf)) for f in fn]])

output = open("data/missing_pdf.txt", "w")
for f in xml_files:
    if f.endswith("-mets"):
        fbis = f[:-5]
    if f not in pdf_files and fbis not in pdf_files:
        output.write(f + "\n")

output2 = open("data/missing_xml.txt", "w")
for f in pdf_files:
    if len(f) == 22:
        fbis = f + "-mets"
    if f not in xml_files and fbis not in xml_files:
        output2.write(f + "\n")
