"""Basis Flask app"""

import json
import math

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
    if query and query == "test":
        query_dic = {"query_string": {"query": query}}
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
                        {"date": {"order": "asc"}}
                    ],
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
            results = json.loads(r.text)
            number = results["hits"]["total"]["value"]
            timing = '{0:.2f}'.format(results["took"]/1000).replace('.', ',')
            if number == 0:
                found_string = "Aucun résultat"
            elif number == 1:
                found_string = "Un seul résultat"
            else:
                nb = '{:,}'.format(number).replace(',', ' ')
                found_string = f"Environ {nb} résultats"
            nbstr = f"{found_string} ({timing} secondes)"
            hits = results["hits"]
            pages = []
            for hit in hits["hits"]:
                page_id = hit["_source"]["page"]
                matches = hit["highlight"]["text"]
                page = {"page_id": page_id, "matches": matches}
                pages.append(page)

            lastp = math.ceil(number/10)
            firstp = min(max(1, p-4), lastp-9)
            html = render_template("results.html", query=query, nbstr=nbstr, pages=pages, p=p, firstp=firstp, lastp=lastp)
        else:
            html = f"HTTP Error: {r.status_code}"
    elif query:
        html = f"<p>Vous avez cherché <b>{query}</b></p>"
        endpoint = cred["endpoint"]
        es_url = f"{endpoint}/pages/_search"
        username = cred["username"]
        password = cred["password"]
        headers = {"Content-Type": "application/json; charset=utf8"}
        size = 10
        fuzzy = request.args.get("fuzzy")
        if fuzzy == "true":
            query_dic = {"fuzzy": {"text": {"value": query}}}
        else:
            query_dic = {"query_string": {"query": query}}
        data =  {
                    "size": size,
                    "sort": [
                        {"date": {"order": "asc"}}
                    ],
                    "query": query_dic,
                    "highlight": {
                        "fields": {
                            "text": {}
                        },
                        "pre_tags": "<strong>",
                        "post_tags": "</strong>",
                        "fragment_size": 200
                    }
                }
        r = requests.post(es_url, auth=(username, password), headers=headers, data=json.dumps(data))
        if r.status_code == 200:
            results = json.loads(r.text)
            number = results["hits"]["total"]["value"]
            if number == 0:
                found_string = "Aucun résultat trouvé."
            elif number == 1:
                found_string = "Un seul résultat trouvé :"
            else:
                found_string = f"{number} résultats trouvés :"
            html += f"<p>{found_string}</p>"
            hits = results["hits"]
            pages = []
            for hit in hits["hits"]:
                page_id = hit["_source"]["page"]
                matches = hit["highlight"]["text"]
                page = {"page_id": page_id, "matches": matches}
                pages.append(page)
            for i, page in enumerate(pages):
                html += f"<p>{i+1}. {page['page_id']}<br><br>"
                for match in page["matches"]:
                    html += f"{match}<br>"
                html += "</p>"
            if len(pages) == size:
                html += "<p>...</p>"
            html += f'<p><form><input type="hidden" name="term" value="{query}">'
            if fuzzy:
                html += '<input type="hidden" name="fuzzy" value="true">'
            html += '<input type="submit" value="Retour"></form></p>'
        else:
            html = f"HTTP Error: {r.status_code}"

    else:
        term = request.args.get("term")
        if not term:
            term = ""
        fuzzy = request.args.get("fuzzy")
        if fuzzy:
            checked = "checked"
        else:
            checked = ""
        html = render_template("search.html", term=term, checked=checked)
    return html

if __name__ == "__main__":
    app.run(debug=True)
