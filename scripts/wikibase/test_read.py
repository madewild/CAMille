"""Reading triples from SPARQuLb"""

from SPARQLWrapper import SPARQLWrapper, JSON
import pywikibot

#connect to the wikibase
wikibase = pywikibot.Site("en", "sparqulb")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

sparql = SPARQLWrapper("https://query.sparq.ulb.be/bigdata/namespace/wdq/sparql")

query = "select ?item ?value where {?item rdfs:label ?value}"

sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
print(results)

bindings = results['results']['bindings']
print(f"{len(bindings)} items found")
for result in bindings:
    qid = result['item']['value'].replace("https://sparq.ulb.be/entity/", "")
    print(qid)
