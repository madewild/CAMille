"""Flatten structure of La Presse by years"""

import os
import shutil

PATH = "/run/media/max/CAMille 1/La Presse/"
NEW_PATH = "/run/media/max/CAMille 1/La Presse_YEARS/"
folders = os.listdir(PATH)

for folder in folders:
    year = folder.split("_")[1][:4]
    year_path = f"{NEW_PATH}{year}/"
    if not os.path.exists(year_path):
        os.makedirs(year_path)
    files = os.listdir(PATH + folder)
    for f in files:
        src_path = f"{PATH}{folder}/{f}"
        if os.path.isfile(src_path):
            dst_path = year_path + f
            shutil.move(src_path, dst_path)
