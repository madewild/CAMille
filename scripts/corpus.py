"""Generate a corpus of random files for class"""

import random
import sys

import boto3

if __name__ == "__main__":
    session = boto3.Session(profile_name='semsol')
    s3 = session.client('s3')
    paginator = s3.get_paginator('list_objects')

    bucket_name = "camille-data"
    code = sys.argv[1]
    start = int(sys.argv[2])
    try:
        end = int(sys.argv[3])
    except IndexError:
        end = start
    years = range(start, end+1)

    for year in years:
        print(f"Processing {year}...")
        prefix = f"TXT/{code}/{year}"
        all_objects = []
        
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        for page in pages:
            try:
                objects = page["Contents"]
                all_objects += objects
            except KeyError:
                print(f"Nothing found for {year}, skipping...")
        random.shuffle(all_objects)
        selected = all_objects[:100]

        for obj in selected:
            key = obj["Key"]
            filename = key.split("/")[-1]
            fullpath = f"data/txt/{filename}"
            s3.download_file(bucket_name, key, fullpath)
