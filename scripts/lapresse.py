"""Explore La Presse dataset"""

import os
import sys

path = "/run/media/max/CAMille 1/La Presse/"
folders = os.listdir(path)
print(f"\n{len(folders)} folders found\n")

years_covered = set()
total_pages = 0

for folder in sorted(folders):
    year = folder.split("_")[1][:4]
    years_covered.add(int(year))
    files = os.listdir(path+folder)
    xmls = set()
    pdfs = set()
    for f in files:
        if f.endswith(".xml"):
            xmls.add(f)
        elif f.endswith(".pdf"):
            pdfs.add(f)
        else:
            print(f"Unknown file extension: {f}")
            sys.exit()
    nb_xml = len(xmls)
    nb_pdf = len(pdfs)
    if nb_pdf == nb_pdf:
        date = folder.split("_")[1]
        edition = "-".join([date[:4], date[4:6], date[6:]])
        print(f"Edition {edition} contains {nb_xml} pages")
        total_pages += nb_xml
    else:
        print(f"Mismatch found in folder {folder}: {nb_xml} XML vs {nb_pdf} PDF")
        sys.exit()

#print(f"\nYears covered: {sorted(years_covered)}")
years_to_cover = range(1954, 1994)
years_not_covered = [y for y in years_to_cover if y not in years_covered]
print(f"Years NOT covered: {years_not_covered}")
print(f"Total number of pages: {total_pages}")
