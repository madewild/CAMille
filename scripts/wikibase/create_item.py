"""Creating a single item"""

import json
import sys

import pywikibot

#connect to the wikibase
wikibase = pywikibot.Site("en", "sparqulb")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

with open("data/sample.json", encoding="utf-8") as json_file:
    sample = json.load(json_file)
    print(sample)

    data = {}

    item = pywikibot.ItemPage(wikibase_repo)
    label = sample['full_name']
    data['labels'] = {'en': label, 'fr': label}
    data['descriptions'] = {'en': "journalist", 'fr': "journaliste"}

    new_claims = []

    # instance of human
    claim = pywikibot.Claim(wikibase_repo, "P3", datatype='wikibase-item')
    object = pywikibot.ItemPage(wikibase_repo, "Q1206")
    claim.setTarget(object)
    new_claims.append(claim.toJSON())

    """# given name
    claim = pywikibot.Claim(wikibase_repo, "P115", datatype='string')
    claim.setTarget(sample['first_name'])
    new_claims.append(claim.toJSON())

    # family name
    claim = pywikibot.Claim(wikibase_repo, "P113", datatype='string')
    claim.setTarget(sample['last_name'])
    new_claims.append(claim.toJSON())"""

    # sex or gender
    claim = pywikibot.Claim(wikibase_repo, "P87", datatype='wikibase-item')
    if sample['gender'] == "H":
        object = pywikibot.ItemPage(wikibase_repo, "Q1173")
        claim.setTarget(object)
        new_claims.append(claim.toJSON())
    elif sample['gender'] == "F":
        object = pywikibot.ItemPage(wikibase_repo, "Q1179")
        claim.setTarget(object)
        new_claims.append(claim.toJSON())
    else:
        print(f"Unknown gender: {sample['gender']}")

    # country of citizenship
    claim = pywikibot.Claim(wikibase_repo, "P89", datatype='wikibase-item')
    if sample['country'] == "Belgique":
        object = pywikibot.ItemPage(wikibase_repo, "Q4")
        claim.setTarget(object)
        new_claims.append(claim.toJSON())
    else:
        print(f"Unknown country: {sample['country']}")

    data['claims'] = new_claims
    item.editEntity(data, summary="adding new journalist")
    print (f"{sample['full_name']} added as {item.getID()}")
