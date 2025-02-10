"""Editing multiple descriptions"""

from SPARQLWrapper import SPARQLWrapper, JSON
import pywikibot

#connect to the wikibase
wikibase = pywikibot.Site("en", "sparqulb")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

sparql = SPARQLWrapper("https://query.sparq.ulb.be/bigdata/namespace/wdq/sparql")

query = f"""select distinct ?s where {{
            ?s wdt:P3 wd:Q1225 .
        }}"""

sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

bindings = results['results']['bindings']
print(f"{len(bindings)} items found\n")
for result in bindings:
    qid = result['s']['value'].replace("https://sparq.ulb.be/entity/", "")
    item = pywikibot.ItemPage(wikibase_repo, qid)
    item.get()
    descriptions = item.descriptions
    if descriptions['fr'] == "journaliste belge":
        new_desc = {'en': 'journalist', 'fr': 'journaliste'}
        item.editDescriptions(new_desc, summary='Description changed')
        print(f"Changing description for {qid}")
