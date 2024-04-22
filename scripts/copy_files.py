"""Copy files to ignore mets"""

import os
import shutil

PATH_XML = "/run/media/max/CAMille 1/JB685/"
PATH_PDF = "/run/media/max/CAMille 1/JB685_PDF/"

xmls = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(PATH_XML)) for f in fn]
xml_files = [f.split("/")[-1][:-4] for f in xmls]

pdfs = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(PATH_PDF)) for f in fn]
pdf_files = [f.split("/")[-1][:-4] for f in pdfs]

xml_files = [f for f in xml_files if len(f) == 27 and not f.endswith("mets")]
pdf_files = [f for f in pdf_files if len(f) == 27 and not f.endswith("mets")]

for f in xml_files:
    f += ".xml"
    src_path = PATH_XML + f
    dst_path = "/run/media/max/CAMille 1/JB685_XML_nomets/" + f
    shutil.copy(src_path, dst_path)

for f in pdf_files:
    f += ".pdf"
    src_path = PATH_PDF + f
    dst_path = "/run/media/max/CAMille 1/JB685_PDF_nomets/" + f
    shutil.copy(src_path, dst_path)
