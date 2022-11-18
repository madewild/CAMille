"""Detect missing years in subcorpus"""

import os

data_path = "data/txt/"
files = os.listdir(data_path)
print(len(files))
all_years = range(1887, 1971)
covered_years = set()
for f in files :
		year = f.split("_")[2].split("-")[0]
		covered_years.add(int(year))
missing_years = [y for y in all_years if y not in covered_years]
print(f"Missing years: {', '.join([str(y) for y in missing_years])}")
