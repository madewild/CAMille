"""Importing items from JSON list"""

import json
import re
import sys

import pywikibot

#connect to the wikibase
wikibase = pywikibot.Site("en", "sparqulb")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

with open("data/json/BDD-final2024_bon_juillet31.xlsx.clean.json", encoding="utf-8") as json_file:
    collection = json.load(json_file)
    nb = len(collection)
    print(f"{nb} journalists found")

    for entry in [collection["0"]]:

        data = {}
        label = entry['full name']
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
        claim.setTarget(entry['given name'])
        new_claims.append(claim.toJSON())

        # family name as string
        claim = pywikibot.Claim(wikibase_repo, "P6099", datatype='string')
        claim.setTarget(entry['family name'])
        new_claims.append(claim.toJSON())

        # sex or gender
        claim = pywikibot.Claim(wikibase_repo, "P87", datatype='wikibase-item')
        if entry['sex'] == "male":
            value = pywikibot.ItemPage(wikibase_repo, "Q1173")
            claim.setTarget(value)
            new_claims.append(claim.toJSON())
        elif entry['sex'] == "female":
            value = pywikibot.ItemPage(wikibase_repo, "Q1179")
            claim.setTarget(value)
            new_claims.append(claim.toJSON())
        else:
            print(f"Unknown gender: {entry['sex']}")

        # country of citizenship
        claim = pywikibot.Claim(wikibase_repo, "P89", datatype='wikibase-item')
        if entry['country'] == "Belgique":
            value = pywikibot.ItemPage(wikibase_repo, "Q4")
            claim.setTarget(value)
            new_claims.append(claim.toJSON())
        else:
            print(f"Unknown country: {entry['country']}")

        # ISNI number
        isni_number = entry['ISNI']
        if isni_number:
            claim = pywikibot.Claim(wikibase_repo, "P218", datatype='external-id')
            claim.setTarget(isni_number)
            new_claims.append(claim.toJSON())

        data['claims'] = new_claims
        try:
            item.editEntity(data, summary="adding new journalist")
            print (f"{entry['full name']} added as {item.getID()}")
        except pywikibot.exceptions.OtherPageSaveError as e:
            x = re.findall(r'\[\[Item:.*\]\]', str(e))
            if x:
                qid =  x[-1].replace("[[Item:", "").split("|")[0]
            else:
                print("QID not found")
            print(f"{label} already exists as {qid}")
    print("")
