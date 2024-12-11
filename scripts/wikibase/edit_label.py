"""Editing a single label"""

import pywikibot

#connect to the wikibase
wikibase = pywikibot.Site("en", "sparqulb")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

qid = 'Q2'
data = {}

item = pywikibot.ItemPage(wikibase_repo, qid)
en_label = item.labels['en']
en_alias = item.aliases['en']
data['labels'] = {'fr': en_label}
data['descriptions'] = {'fr': "université belge francophone"}
data['aliases'] = {'fr': en_alias}
item.editEntity(data)
