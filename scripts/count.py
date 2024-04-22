"""Count files for given journal"""

import os

PATH_XML = "/run/media/max/CAMille 1/JB685_XML_nomets/"
PATH_PDF = "/run/media/max/CAMille 1/JB685_PDF_nomets/"

xmls = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(PATH_XML)) for f in fn]
xml_files = [f.split("/")[-1][:-4] for f in xmls]

pdfs = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(PATH_PDF)) for f in fn]
pdf_files = [f.split("/")[-1][:-4] for f in pdfs]

xml_files = [f for f in xml_files if len(f) == 27 and not f.endswith("mets")]
pdf_files = [f for f in pdf_files if len(f) == 27 and not f.endswith("mets")]

print(f"{len(xml_files)} XML files found")
print(f"{len(pdf_files)} PDF files found")
