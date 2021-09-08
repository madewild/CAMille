"""Basic Flask app"""

import calendar
import json
import locale
import math
from pathlib import Path
from unidecode import unidecode
from zipfile import ZipFile

import boto3

from flask import Flask, request, render_template, send_file
from flask_htpasswd import HtPasswdAuth

import requests

try:
    cred = json.load(open("credentials.json"))
except FileNotFoundError:
    cred = json.load(open("/var/www/camille/credentials.json"))

locale.setlocale(locale.LC_ALL, 'fr_BE.utf8')

app = Flask(__name__)
app.config['FLASK_HTPASSWD_PATH'] = '/etc/apache2/.htpasswd'
app.config['FLASK_AUTH_ALL'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

htpasswd = HtPasswdAuth(app)

@app.template_filter()
def strip_param(long_url, param):
    new_url = long_url.replace(param, "")
    return new_url

@app.route("/")
def hello():
    query = request.args.get("query")
    if query:

        sortcrit = request.args.get("sortcrit")
        if sortcrit:
            if sortcrit == "datedesc":
                sort = [{"date": {"order": "desc"}}]
            elif sortcrit =="dateasc":
                sort = [{"date": {"order": "asc"}}]
            else:
                sort = ["_score", {"date": {"order": "asc"}}]
        else:
            sortcrit = "relevance"
            sort = ["_score", {"date": {"order": "asc"}}]

        query_dic = {"bool": {"must": [{"query_string": {"query": query}}]}}
        query_dic["bool"]["filter"] = []

        paper = request.args.get("paper")
        if paper:
            query_dic["bool"]["filter"].append({"match": {"journal": paper}})

        year_from = request.args.get("year_from")
        year_to = request.args.get("year_to")
        if year_from:
            query_dic["bool"]["must"].append({"range": {"year": {"gte": year_from, "lte": year_to}}})
        
        month = request.args.get("month")
        if month:
            query_dic["bool"]["filter"].append({"match": {"month": month}})

        day_from = request.args.get("day_from")
        day_to = request.args.get("day_to")
        if day_from:
            query_dic["bool"]["must"].append({"range": {"day": {"gte": day_from, "lte": day_to}}})

        dow = request.args.get("dow")
        if dow:
            query_dic["bool"]["filter"].append({"match": {"dow": dow}})

        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        if date_from:
            query_dic["bool"]["must"].append({"range": {"date": {"gte": date_from, "lte": date_to}}})

        edition = request.args.get("edition")
        if edition:
            query_dic["bool"]["filter"].append({"match": {"edition": edition}})

        page_from = request.args.get("page_from")
        page_to = request.args.get("page_to")
        if page_from:
            query_dic["bool"]["must"].append({"range": {"pagenb": {"gte": page_from, "lte": page_to}}})

        language = request.args.get("language")
        if language:
            query_dic["bool"]["filter"].append({"match": {"language": language}})

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
                    "sort": sort,
                    "track_total_hits": "true",
                    "query": query_dic,
                    "highlight": {
                        "fields": {
                            "text": {}
                        },
                        "pre_tags": "<span class='serp__match'>",
                        "post_tags": "</span>",
                        "fragment_size": 500
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
            with open(path, encoding="utf-8") as f:
                names = json.load(f)
            papers = [{"code": code, "name": names[code]} for code in names]
            if paper:
                matched_papers = [x for x in papers if x["code"] == paper]
            else:
                matched_papers = papers

            months = [{"code": f"{i:02d}", "name": calendar.month_name[i]} for i in range(1, 13)]
            if month:
                matched_months = [x for x in months if x["code"] == month]
            else:
                matched_months = months

            dows = [{"code": f"{i+1}", "name": calendar.day_name[i]} for i in range(7)]
            if dow:
                matched_dows = [x for x in dows if x["code"] == dow]
            else:
                matched_dows = dows

            editions = [{"code": f"{i:02d}", "name": f"{i}e édition"} for i in range(1, 6)]
            editions += [{"code": i, "name": f"{i[1]}e édition spéciale"} for i in ["11", "12"]]
            if edition:
                matched_editions = [x for x in editions if x["code"] == edition]
            else:
                matched_editions = editions

            languages = [{"code": "fr-BE", "name": "français"}]
            if language:
                matched_languages = [x for x in languages if x["code"] == language]
            else:
                matched_languages = languages
            
            for hit in hits["hits"]:
                result_id = hit["_source"]["page"]
                elements = result_id.split("_")
                np = elements[1]
                name = names[np]
                hit_date = elements[2]
                hit_dates = hit_date.split("-")
                hit_year = hit_dates[0]
                hit_month = hit_dates[1]
                hit_day = hit_dates[2]
                edpage = elements[3]
                page = int(edpage.split("-")[1])
                display = f"{name} ({hit_day}/{hit_month}/{hit_year} - p. {page})"
                try:            
                    matches = hit["highlight"]["text"]
                except KeyError: # no matches (wildcard), defaulting to 500 first chars
                    matches = [hit["_source"]["text"][:500] + "..."]
                all_matches = " [...] ".join(matches)
                all_matches = all_matches.replace("<span", "##!!##").replace("</span", "!!##!!").replace("<", "")
                all_matches = all_matches.replace("##!!##", "<span").replace("!!##!!", "</span")
                result = {"id": result_id, "display": display, "matches": all_matches}
                results.append(result)

            maxp = math.ceil(number/10)
            firstp = max(1, min(p-4, maxp-9))
            lastp = min(firstp+10, maxp+1)

            doc = request.args.get("doc")
            if doc:
                s3 = boto3.client('s3')
                bucket_name = "camille-data"
                elements = doc.split("_")
                np = elements[1]
                doc_date = elements[2]
                doc_year = doc_date.split("-")[0]
                key = f"PDF/{np}/{doc_year}/{doc}.pdf"
                temp_path = Path(__file__).parent / f"static/temp/{doc}.pdf"
                s3.download_file(bucket_name, key, str(temp_path))
            else:
                doc = "false"

            url = request.url
            if "&p=" in url:
                url = url.split("&p=")[0]

            export = request.args.get("export")
            if export:
                data2 =  {
                    "size": 500,
                    "query": query_dic,
                    "sort": sort
                }
                r2 = requests.post(es_url, auth=(username, password), headers=headers, data=json.dumps(data2))
                if r2.status_code == 200:
                    resdic2 = json.loads(r2.text)
                    hits2 = resdic2["hits"]
                    query_norm = unidecode(query).replace(" ", "_")
                    query_norm = "".join([c for c in query_norm if c.isalpha() or c == "_"])
                    zippath = Path(__file__).parent / f"static/temp/camille_{query_norm}.zip"
                    with ZipFile(zippath, 'w') as myzip:
                        readme = abspath = Path(__file__).parent / f"static/README.txt"
                        myzip.write(abspath, "_README.txt")
                        for hit in hits2["hits"]:
                            result_id = hit["_source"]["page"]
                            text = hit["_source"]["text"]
                            arcpath = f"{result_id}.txt"
                            abspath = Path(__file__).parent / f"static/temp/{arcpath}"
                            with open(abspath, "w", encoding="utf-8") as f:
                                f.write(text)
                            myzip.write(abspath, arcpath)
                            abspath.unlink()
                    return send_file(zippath, as_attachment=True)

            html = render_template("results.html", query=query, stats=stats,
                                   results=results, p=p, firstp=firstp, lastp=lastp, 
                                   maxp=maxp, doc=doc, url=url, papers=matched_papers,
                                   number=number, sortcrit=sortcrit, paper=paper,
                                   year_from=year_from, year_to=year_to, months=matched_months,
                                   month=month, dows=matched_dows, dow=dow, editions=matched_editions, 
                                   edition=edition, languages=matched_languages, language=language,
                                   page_from=page_from, page_to=page_to, day_from=day_from, day_to=day_to,
                                   date_from=date_from, date_to=date_to
                                  )
        else:
            html = f"HTTP Error: {r.status_code}"
    else:
        page = request.args.get("page")
        if page:
            if page == "about":
                html = render_template("about.html")
            elif page == "resources":
                html = render_template("resources.html")
            elif page == "contact":
                html = render_template("contact.html")
            elif page == "help":
                html = render_template("help.html")
            else:
                html = render_template("404.html")
        else:
            html = render_template("search.html")
    return html

if __name__ == "__main__":
    app.run(debug=True)
