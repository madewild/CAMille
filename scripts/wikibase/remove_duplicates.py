"""Example script for removing duplicate claims"""

import sys

import requests
from SPARQLWrapper import SPARQLWrapper, JSON

import pywikibot

prop_id = sys.argv[1]

api_url = f"https://sparq.ulb.be/w/api.php?action=wbgetentities&props=labels&format=json&ids={prop_id}"
resp = requests.get(api_url, timeout=60)
prop_name = resp.json()["entities"][prop_id]["labels"]["en"]["value"]

#connect to the wikibase
wikibase = pywikibot.Site("en", "sparqulb")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

sparql = SPARQLWrapper("http://query.sparq.ulb.be/bigdata/namespace/wdq/sparql")
query = """
    select ?item where {
        ?item <https://sparq.ulb.be/prop/direct/P3> <https://sparq.ulb.be/entity/Q3> .
    }
"""
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

bindings = results['results']['bindings']
print(f"{len(bindings)} items found")
for result in bindings:
    qid = result['item']['value'].replace("https://sparq.ulb.be/entity/", "")
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
