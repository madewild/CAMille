"""Basis Flask app"""

import json

from flask import Flask, request
import requests

app = Flask(__name__)
@app.route("/")
def hello():
    query = request.args.get("query")
    if query:
        html = f"<p>Vous avez cherché <b>{query}</b></p>"
        try:
            cred = json.load(open("es_credentials.json"))
        except FileNotFoundError:
            cred = json.load(open("/var/www/camille/es_credentials.json"))
        endpoint = cred["endpoint"]
        es_url = f"{endpoint}/pages/_search"
        username = cred["username"]
        password = cred["password"]
        headers = {"Content-Type": "application/json; charset=utf8"}
        data =  {
                    "size": 20,
                    "sort": [
                        {"date": {"order": "asc"}}
                    ],
                    "query": {
                        "query_string": {
                            "query": query
                        }
                    },
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
            if len(pages) == 20:
                html += "<p>...</p>"
            html += '<p><form><input type="submit" value="Retour"></form></p>'
        else:
            html = f"HTTP Error: {r.status_code}"

    else:
        html = """<h1>CAMILLE</h1>
                <h2>Centre d'Archives sur les Médias et l'Information</h2>
                <p><form>
                <label for="query">Faites une recherche :</label> 
                <input type="text" id="query" name="query"> 
                <input type="submit" value="OK">
                </form></p>
            """
    return html
if __name__ == "__main__":
    app.run(debug=True)
