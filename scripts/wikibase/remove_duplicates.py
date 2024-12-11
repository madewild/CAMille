"""Example script for removing duplicate claims"""

import sys
import pywikibot

qid = sys.argv[1]
try:
    pid = sys.argv[2]
except IndexError:
    pid = False

#connect to the wikibase
wikibase = pywikibot.Site("en", "sparqulb")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

item = pywikibot.ItemPage(wikibase_repo, qid)
all_claims = []
try:
    if pid:
        pid_list = [pid]
    else:
        pid_list = item.claims
    for prop_id in pid_list:
        for claim in item.claims[prop_id]:
            claim_value = claim.toJSON().get('mainsnak').get('datavalue').get('value')
            if claim_value in all_claims: # duplicate detected
                item.removeClaims(claim, summary=u"Removing duplicate property")
                print(f"Removing duplicate {prop_id} for {qid}")
            else:
                all_claims.append(claim_value)
except KeyError: # no claim, should not happen
    print(f"No {prop_id} found for {qid}")
