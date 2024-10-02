"""Creating a single item"""

import json

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
    if sample['country'] == "Belgique":
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
    claim.setTarget(sample['first_name'])
    new_claims.append(claim.toJSON())

    # family name as string
    claim = pywikibot.Claim(wikibase_repo, "P6099", datatype='string')
    claim.setTarget(sample['last_name'])
    new_claims.append(claim.toJSON())

    # sex or gender
    claim = pywikibot.Claim(wikibase_repo, "P87", datatype='wikibase-item')
    if sample['gender'] == "H":
        value = pywikibot.ItemPage(wikibase_repo, "Q1173")
        claim.setTarget(value)
        new_claims.append(claim.toJSON())
    elif sample['gender'] == "F":
        value = pywikibot.ItemPage(wikibase_repo, "Q1179")
        claim.setTarget(value)
        new_claims.append(claim.toJSON())
    else:
        print(f"Unknown gender: {sample['gender']}")

    # country of citizenship
    claim = pywikibot.Claim(wikibase_repo, "P89", datatype='wikibase-item')
    if sample['country'] == "Belgique":
        value = pywikibot.ItemPage(wikibase_repo, "Q4")
        claim.setTarget(value)
        new_claims.append(claim.toJSON())
    else:
        print(f"Unknown country: {sample['country']}")

    data['claims'] = new_claims
    item.editEntity(data, summary="adding new journalist")
    print (f"{sample['full_name']} added as {item.getID()}")
