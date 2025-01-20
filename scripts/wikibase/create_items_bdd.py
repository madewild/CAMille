"""Importing items from JSON list"""

import json
import re
import sys

from SPARQLWrapper import SPARQLWrapper, JSON
import pywikibot

#connect to the wikibase
wikibase = pywikibot.Site("en", "sparqulb")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

sparql = SPARQLWrapper("https://query.sparq.ulb.be/bigdata/namespace/wdq/sparql")

cutoff = sys.argv[1]
if "-" in cutoff:
    start = int(cutoff.split("-")[0])
    end = int(cutoff.split("-")[1])
else:
    start = 0
    end = int(cutoff)

FILE = "BDD-final2024_bon_juillet31.xlsx.clean.json"
LIMIT = 15000

def format_date(date_string):
    if len(date_string) == 10:
        year = date_string[:4]
        month = date_string[5:7]
        day = date_string[8:]
        if day == "00":
            target = pywikibot.WbTime(site=wikibase_repo, year=int(year), month=int(month))
        else:
            target = pywikibot.WbTime(site=wikibase_repo, year=int(year), month=int(month), day=int(day))
    elif len(date_string) == 7:
        year = date_string[:4]
        month = date_string[5:7]
        target = pywikibot.WbTime(site=wikibase_repo, year=int(year), month=int(month))
    elif len(date_string) == 4:
        year = date_string
        target = pywikibot.WbTime(site=wikibase_repo, year=int(year))
    return target

with open(f"data/json/{FILE}", encoding="utf-8") as json_file:
    collection = json.load(json_file)
    nb = len(collection)
    print(f"\n{nb} journalists found")

    for entry in [collection[f"{n}"] for n in range(start, end)]:

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
        data['aliases'] = {'en': []}
        aliases = entry['alias']
        if aliases:
            for alias in aliases:
                data['aliases']['en'].append(alias)
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
        given = entry['given name']
        if given: # some people have only a family name (e.g. "Allaer")
            claim = pywikibot.Claim(wikibase_repo, "P6098", datatype='string')
            claim.setTarget(given)
            new_claims.append(claim.toJSON())

        # family name as string
        claim = pywikibot.Claim(wikibase_repo, "P6099", datatype='string')
        claim.setTarget(entry['family name'])
        new_claims.append(claim.toJSON())

        # sex or gender
        claim = pywikibot.Claim(wikibase_repo, "P87", datatype='wikibase-item')
        sex = entry['sex']
        if sex:
            if sex == "male":
                value = pywikibot.ItemPage(wikibase_repo, "Q1173")
                claim.setTarget(value)
                new_claims.append(claim.toJSON())
            elif sex == "female":
                value = pywikibot.ItemPage(wikibase_repo, "Q1179")
                claim.setTarget(value)
                new_claims.append(claim.toJSON())
            else:
                print(f"Unknown gender: {sex}")
                sys.exit()

        # country of citizenship
        claim = pywikibot.Claim(wikibase_repo, "P89", datatype='wikibase-item')
        country = entry['country']
        if country:
            query = f"""select * where {{
                        ?country wdt:P3 wd:Q1605 .
                        ?country rdfs:label "{country}"@fr .
                    }}"""
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            bindings = results['results']['bindings']
            qids = []
            for result in bindings:
                qid = result['country']['value'].replace("https://sparq.ulb.be/entity/", "")
                qids.append(qid)
            if len(qids) == 0:
                print(f"No QID found for {country}")
                sys.exit()
            elif len(qids) > 1 : 
                print(f"More than one QID found for {country}: {qids}")
                sys.exit()
            else:
                country_qid = qids[0]         
                value = pywikibot.ItemPage(wikibase_repo, country_qid)
                claim.setTarget(value)
                new_claims.append(claim.toJSON())

        # ISNI number: problem in BDD file!
        """isni_number = entry['ISNI']
        if isni_number:
            claim = pywikibot.Claim(wikibase_repo, "P218", datatype='external-id')
            claim.setTarget(isni_number)
            new_claims.append(claim.toJSON())"""

        # occupations
        occupations = entry['occupation']
        if occupations:
            for occupation in occupations:
                claim = pywikibot.Claim(wikibase_repo, "P6100", datatype='string')
                claim.setTarget(occupation)
                new_claims.append(claim.toJSON())

        # medias
        medias = entry['media']
        if medias:
            for media in medias:
                claim = pywikibot.Claim(wikibase_repo, "P8682", datatype='string')
                media_name = media["name"]
                claim.setTarget(media_name)
                media_type = media["type"]
                if media_type == "unsure":
                    qualifier = pywikibot.Claim(wikibase_repo, "P1111") # sourcing circumstances
                    target = pywikibot.ItemPage(wikibase_repo, "Q9743") # presumably
                    qualifier.setTarget(target)
                    claim.addQualifier(qualifier)
                new_claims.append(claim.toJSON())

        # works
        works = entry['work']
        if works:
            for work in works:
                if len(work) < LIMIT:
                    claim = pywikibot.Claim(wikibase_repo, "P8683", datatype='string')
                    claim.setTarget(work)
                    new_claims.append(claim.toJSON())
                else:
                    print(f"Work is longer than {LIMIT} chars, aborting")
                    sys.exit()

        # notice
        notices = entry['notice']
        if notices:
            for notice in notices:
                if len(notice) < LIMIT:
                    claim = pywikibot.Claim(wikibase_repo, "P8684", datatype='string')
                    claim.setTarget(notice)
                    new_claims.append(claim.toJSON())
                else:
                    print(f"Notice is longer than {LIMIT} chars, skipping")

        # sources
        sources = entry['source']
        if sources:
            for source in sources:
                texts = source["text"]
                for text in texts:
                    claim = pywikibot.Claim(wikibase_repo, "P8722", datatype='string')
                    claim.setTarget(text)
                    new_claims.append(claim.toJSON())

        # BDD ID
        bdd_id = entry['ID']
        if bdd_id:
            claim = pywikibot.Claim(wikibase_repo, "P8852", datatype='external-id')
            claim.setTarget(bdd_id[0])
            new_claims.append(claim.toJSON())

        # place of birth
        pob = entry['place of birth']
        if pob:
            claim = pywikibot.Claim(wikibase_repo, "P8678", datatype='string')
            claim.setTarget(pob)
            new_claims.append(claim.toJSON())

        # place of death
        pod = entry['place of death']
        if pod:
            claim = pywikibot.Claim(wikibase_repo, "P8679", datatype='string')
            claim.setTarget(pod)
            new_claims.append(claim.toJSON())

        # date of birth
        dob = entry['date of birth']
        if dob:
            claim = pywikibot.Claim(wikibase_repo, "P4817", datatype='time')
            target = format_date(dob)
            claim.setTarget(target)
            new_claims.append(claim.toJSON())

        # date of death
        dod = entry['date of death']
        if dod:
            claim = pywikibot.Claim(wikibase_repo, "P4535", datatype='time')
            target = format_date(dod)
            claim.setTarget(target)
            new_claims.append(claim.toJSON())

        # work period
        periods = entry['work period']
        if periods:
            for period in periods:
                claim = pywikibot.Claim(wikibase_repo, "P6157", datatype='string')
                claim.setTarget(period)
                new_claims.append(claim.toJSON())

        # affiliations
        affiliations = entry['affiliation']
        if affiliations:
            for affiliation in affiliations:
                claim = pywikibot.Claim(wikibase_repo, "P8680", datatype='string')
                aff_name = affiliation["name"]
                if not aff_name: # handle edge case when role known but not assoc
                    aff_name = "inconnu"
                claim.setTarget(aff_name)
                aff_role = affiliation["role"]
                if aff_role:
                    qualifier = pywikibot.Claim(wikibase_repo, "P8681")
                    qualifier.setTarget(aff_role)
                    claim.addQualifier(qualifier)
                aff_period = affiliation["period"]
                if aff_period:
                    qualifier = pywikibot.Claim(wikibase_repo, "P6157")
                    qualifier.setTarget(aff_period)
                    claim.addQualifier(qualifier)
                new_claims.append(claim.toJSON())

        data['claims'] = new_claims
        try:
            item.editEntity(data, summary="adding new journalist")
            print (f"{label} added as {item.getID()}")
        except pywikibot.exceptions.OtherPageSaveError as e:
            x = re.findall(r'\[\[Item:.*\]\]', str(e))
            if not x:
                print("QID not found")
                sys.exit()
            else:
                if "-1" in x [-1]: # error not due to item already created
                    print(data)
                    sys.exit()
                else:
                    qid =  x[-1].replace("[[Item:", "").split("|")[0]
                    print(f"{label} already exists as {qid}\n")
                    existing_item = pywikibot.ItemPage(wikibase_repo, qid)
                    if data["aliases"]["en"]:
                        existing_item.editEntity({'aliases': data["aliases"]}, summary=f"adding aliases")
                    added_claims = []
                    for claim in new_claims:
                        property = claim['mainsnak']['property']
                        if property in existing_item.claims:
                            pass
                            # print(f"{property} already present for {label}")
                            # compare claims to check if changed and merge if needed
                        else:
                            print(f"{property} is a new claim for {label}, adding")
                            existing_item.editEntity({'claims': [claim]}, summary=f"adding {property}")

    print("")
