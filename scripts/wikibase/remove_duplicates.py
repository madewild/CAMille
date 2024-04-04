"""Example script for removing duplicate claims"""

import sys

import requests
from SPARQLWrapper import SPARQLWrapper, JSON

import pywikibot

en_type = sys.argv[1]
country = sys.argv[2]
prop_id = sys.argv[3]

api_url = f"https://linkedopendata.eu/w/api.php?action=wbgetentities&props=labels&format=json&ids={prop_id}"
resp = requests.get(api_url, timeout=60)
prop_name = resp.json()["entities"][prop_id]["labels"]["en"]["value"]

#connect to the wikibase
wikibase = pywikibot.Site("my", "my")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

if en_type == "proj":
    ent = "Q9934"
elif en_type == "benef":
    ent = "Q196899"
elif en_type == "field":
    ent = "Q200769"
elif en_type == "prog":
    ent = "Q2463047"
else:
    print("Unknown entity type")
    sys.exit()

sparql = SPARQLWrapper("http://query.linkedopendata.eu/bigdata/namespace/wdq/sparql")
if en_type == "field":
    query = """
            select ?item where {
                ?item <https://linkedopendata.eu/prop/direct/P35> <https://linkedopendata.eu/entity/""" + ent + """> .
            }
        """
else:
    query = f"""select DISTINCT ?item where {{
                    ?item <https://linkedopendata.eu/prop/direct/P35> <https://linkedopendata.eu/entity/{ent}> .
                    ?item <https://linkedopendata.eu/prop/direct/P32> <https://linkedopendata.eu/entity/{country}> .
                    ?item <https://linkedopendata.eu/prop/direct/{prop_id}> ?value .
                }}"""
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

bindings = results['results']['bindings']
print(f"{len(bindings)} items found")
for result in bindings:
    qid = result['item']['value'].replace("https://linkedopendata.eu/entity/", "")
    item = pywikibot.ItemPage(wikibase_repo, qid)
    item.get()
    all_claims = []
    try:
        for claim in item.claims[prop_id]:
            claim_value = claim.toJSON().get('mainsnak').get('datavalue').get('value')
            try:
                lang = claim_value["language"]
            except KeyError:
                lang = ""
            if claim_value in all_claims: # duplicate detected
                item.removeClaims(claim, summary=f"Removing duplicate {lang} {prop_name}")
                print(f"Removing duplicate {lang} {prop_name} for {qid}")
            else:
                all_claims.append(claim_value)
    except KeyError: # no claim, should not happen
        print(f"No {prop_name} found for {qid}")
