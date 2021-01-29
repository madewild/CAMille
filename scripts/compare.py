"""Compare XML and PDF"""

import os

path_xml = "/run/media/max/Backup Plus/BelgicaPress XML/"
path_pdf = "/run/media/max/Backup Plus/BelgicaPress PDF/"

xml_files = [f.split("/")[-1][:-4] for f in [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(path_xml)) for f in fn]]
pdf_files = [f.split("/")[-1][:-4] for f in [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(path_pdf)) for f in fn]]

output = open("data/missing_pdf.txt", "w")
for f in xml_files:
    if f not in pdf_files:
        output.write(f + "\n")
