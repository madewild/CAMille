"""Importing items from JSON list"""

import json
import re

import pywikibot

#connect to the wikibase
wikibase = pywikibot.Site("en", "sparqulb")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

with open("data/sample.json", encoding="utf-8") as json_file:
    sample = json.load(json_file)

    for entry in sample:

        data = {}
        label = entry['full_name']
        print(f"\nAttempting import of {label}")

        item = pywikibot.ItemPage(wikibase_repo)
        data['labels'] = {'en': label, 'fr': label}
        if entry['country'] == "Belgique":
            en_desc = "Belgian journalist"
            fr_desc = "journaliste belge"
        else:
            en_desc = "journalist"
            fr_desc = "journaliste"
        data['descriptions'] = {'en': en_desc, 'fr': fr_desc}

        new_claims = []

        # instance of human
        claim = pywikibot.Claim(wikibase_repo, "P3", datatype='wikibase-item')
        value = pywikibot.ItemPage(wikibase_repo, "Q1206")
        claim.setTarget(value)
        new_claims.append(claim.toJSON())

        # instance of journalist
        claim = pywikibot.Claim(wikibase_repo, "P3", datatype='wikibase-item')
        value = pywikibot.ItemPage(wikibase_repo, "Q1225")
        claim.setTarget(value)
        new_claims.append(claim.toJSON())

        # given name as string
        claim = pywikibot.Claim(wikibase_repo, "P6098", datatype='string')
        claim.setTarget(entry['first_name'])
        new_claims.append(claim.toJSON())

        # family name as string
        claim = pywikibot.Claim(wikibase_repo, "P6099", datatype='string')
        claim.setTarget(entry['last_name'])
        new_claims.append(claim.toJSON())

        # sex or gender
        claim = pywikibot.Claim(wikibase_repo, "P87", datatype='wikibase-item')
        if entry['gender'] == "H":
            value = pywikibot.ItemPage(wikibase_repo, "Q1173")
            claim.setTarget(value)
            new_claims.append(claim.toJSON())
        elif entry['gender'] == "F":
            value = pywikibot.ItemPage(wikibase_repo, "Q1179")
            claim.setTarget(value)
            new_claims.append(claim.toJSON())
        else:
            print(f"Unknown gender: {entry['gender']}")

        # country of citizenship
        claim = pywikibot.Claim(wikibase_repo, "P89", datatype='wikibase-item')
        if entry['country'] == "Belgique":
            value = pywikibot.ItemPage(wikibase_repo, "Q4")
            claim.setTarget(value)
            new_claims.append(claim.toJSON())
        else:
            print(f"Unknown country: {entry['country']}")

        data['claims'] = new_claims
        try:
            item.editEntity(data, summary="adding new journalist")
            print (f"{entry['full_name']} added as {item.getID()}")
        except pywikibot.exceptions.OtherPageSaveError as e:
            x = re.findall(r'\[\[Item:.*\]\]', str(e))
            if x:
                qid =  x[-1].replace("[[Item:", "").split("|")[0]
            else:
                print("QID not found")
            print(f"{label} already exists as {qid}")
    print("")
