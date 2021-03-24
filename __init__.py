"""Basis Flask app"""

import json
import math
from pathlib import Path


import boto3

from flask import Flask, request, render_template
from flask_htpasswd import HtPasswdAuth

import requests

try:
    cred = json.load(open("credentials.json"))
except FileNotFoundError:
    cred = json.load(open("/var/www/camille/credentials.json"))

app = Flask(__name__)
app.config['FLASK_HTPASSWD_PATH'] = '/etc/apache2/.htpasswd'
app.config['FLASK_AUTH_ALL'] = True

htpasswd = HtPasswdAuth(app)

@app.route("/")
def hello():
    query = request.args.get("query")
    if query:

        fuzzy = request.args.get("fuzzy")
        journal = request.args.get("journal")
        if fuzzy == "true":
            query_dic = {"fuzzy": {"text": {"value": query}}}
        elif journal:
            query_dic = {"bool": {"must": [{"query_string": {"query": query}}], "filter": [{"match": {"journal": journal}}]}}
        else:
            fuzzy = "false"
            query_dic = {"query_string": {"query": query}}

        complex = "false"
        if any([term in query for term in ['"', ' ', '-']]):
            complex = "true"

        endpoint = cred["endpoint"]
        es_url = f"{endpoint}/pages/_search"
        username = cred["username"]
        password = cred["password"]
        headers = {"Content-Type": "application/json; charset=utf8"}
        size = 10
        p = request.args.get("p")
        if p:
            p = int(p)
        else:
            p = 1
        fromp = (int(p)-1)*10
        data =  {
                    "from": fromp,
                    "size": size,
                    "sort": [
                        "_score",
                        {"date": {"order": "asc"}}
                    ],
                    "track_total_hits": "true",
                    "query": query_dic,
                    "highlight": {
                        "fields": {
                            "text": {}
                        },
                        "pre_tags": "<span class='serp__match'>",
                        "post_tags": "</span>",
                        "fragment_size": 200
                    }
                }
        r = requests.post(es_url, auth=(username, password), headers=headers, data=json.dumps(data))
        if r.status_code == 200:
            resdic = json.loads(r.text)
            number = resdic["hits"]["total"]["value"]
            timing = '{0:.2f}'.format(resdic["took"]/1000).replace('.', ',')
            if number == 0:
                found_string = "Aucun résultat"
            elif number == 1:
                found_string = "Un seul résultat"
            elif p == 1:
                nb = '{:,}'.format(number).replace(',', ' ')
                found_string = f"{nb} résultats"
            else:
                nb = '{:,}'.format(number).replace(',', ' ')
                found_string = f"Page {p} sur {nb} résultats"
            stats = f"{found_string} ({timing} secondes)"
            hits = resdic["hits"]
            results = []
            path = Path(__file__).parent / "static/newspapers.json"
            print(path)
            with open(path) as f:
                names = json.load(f)
            papers = [{"code": code, "name": names[code]} for code in names]
            for hit in hits["hits"]:
                result_id = hit["_source"]["page"]
                elements = result_id.split("_")
                journal = elements[1]
                name = names[journal]
                date = elements[2]
                dates = date.split("-")
                year = dates[0]
                month = dates[1]
                day = dates[2]
                edpage = elements[3]
                page = int(edpage.split("-")[1])
                display = f"{name} ({day}/{month}/{year} - p. {page})"                
                matches = hit["highlight"]["text"]
                result = {"id": result_id, "display": display, "matches": " ... ".join(matches)}
                results.append(result)

            maxp = math.ceil(number/10)
            firstp = max(1, min(p-4, maxp-9))
            lastp = min(firstp+10, maxp+1)

            doc = request.args.get("doc")
            if doc:
                s3 = boto3.client('s3')
                bucket_name = "camille-data"
                elements = doc.split("_")
                journal = elements[1]
                date = elements[2]
                year = date.split("-")[0]
                key = f"PDF/{journal}/{year}/{doc}.pdf"
                s3.download_file(bucket_name, key, f"static/temp/{doc}.pdf")
            else:
                doc = "false"
            url = request.url
            if "&p=" in url:
                url = url.split("&p=")[0]
            html = render_template("results.html", query=query, fuzzy=fuzzy, complex=complex, 
                                   stats=stats, results=results, p=p, firstp=firstp, lastp=lastp, 
                                   maxp=maxp, doc=doc, url=url,papers=papers
                                  )
        else:
            html = f"HTTP Error: {r.status_code}"
    else:
        term = request.args.get("term")
        if not term:
            term = ""
        html = render_template("search.html", term=term)
    return html

if __name__ == "__main__":
    app.run(debug=True)
