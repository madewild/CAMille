"""Script for removing all claims related to one property"""

import sys

from SPARQLWrapper import SPARQLWrapper, JSON
import pywikibot

pid = sys.argv[1]

#connect to the wikibase
wikibase = pywikibot.Site("en", "sparqulb")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

sparql = SPARQLWrapper("https://query.sparq.ulb.be/bigdata/namespace/wdq/sparql")

query = f"""select * where {{
            ?s wdt:P3 wd:Q1225 .
            ?s wdt:{pid} ?value .
        }}"""

sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

bindings = results['results']['bindings']
print(f"{len(bindings)} items found\n")
for result in bindings:
    qid = result['s']['value'].replace("https://sparq.ulb.be/entity/", "")
    item = pywikibot.ItemPage(wikibase_repo, qid)
    for claim in item.claims[pid]:
        claim_value = claim.toJSON().get('mainsnak').get('datavalue').get('value')
        item.removeClaims(claim, summary=u"Removing property")
        print(f"Removing property {pid} for {qid}")
