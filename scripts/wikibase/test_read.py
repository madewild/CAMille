"""Reading triples from SPARQuLb"""

from SPARQLWrapper import SPARQLWrapper, JSON
import pywikibot

#connect to the wikibase
wikibase = pywikibot.Site("en", "sparqulb")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

sparql = SPARQLWrapper("https://query.sparq.ulb.be/bigdata/namespace/wdq/sparql")

query = """select * where {
            ?journalist wdt:P3 wd:Q1225 .
            ?journalist rdfs:label ?name .
            FILTER(lang(?name)="fr")
        }"""

sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

bindings = results['results']['bindings']
print(f"{len(bindings)} items found\n")
for result in bindings:
    print(result['name']['value'])

