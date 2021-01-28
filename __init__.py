"""Basis Flask app"""

import json

from flask import Flask, request
import requests

cred = json.load(open("es_credentials.json"))
endpoint = cred["endpoint"]
es_url = f"{endpoint}/pages/_search"
username = cred["username"]
password = cred["password"]

app = Flask(__name__)
@app.route("/")
def hello():
    query = request.args.get("query")
    if query:
        html = f"<p>Vous avez cherché <b>{query}</b></p>"
        full_es_url = f"{es_url}?q={query}"
        r = requests.get(full_es_url, auth=(username, password))
        if r.status_code == 200:
            results = json.loads(r.text)
            number = results["hits"]["total"]["value"]
            html += f"<p>{number} résultats trouvés :</p>"
            hits = results["hits"]
            pages = []
            for hit in hits["hits"]:
                page = hit["_source"]["page"]
                pages.append(page)
            for i, pid in enumerate(sorted(pages)):
                html += f"{i+1} {pid}<br>"
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
