"""Main Flask app serving search engine"""

import calendar
from collections import defaultdict
import json
import locale
import math
from pathlib import Path
from shutil import copy
import sys
from zipfile import ZipFile

from flask import Flask, request, render_template, send_file, redirect
#from flask_htpasswd import HtPasswdAuth

import pandas as pd
from unidecode import unidecode

from elasticsearch import Elasticsearch

try:
    cred = json.load(open("credentials.json", encoding="utf-8"))
except FileNotFoundError:
    cred = json.load(open("/var/www/camille/credentials.json", encoding="utf-8"))

locale.setlocale(locale.LC_ALL, 'fr_BE.utf8')

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# comment next 3 lines to disable htpasswd (e.g. if CAS is enabled)
#app.config['FLASK_HTPASSWD_PATH'] = '/etc/apache2/.htpasswd'
#app.config['FLASK_AUTH_ALL'] = True
#htpasswd = HtPasswdAuth(app)

@app.template_filter()
def strip_param(long_url, param):
    """Remove parameter from URL"""
    new_url = long_url.replace(param, "")
    return new_url

@app.route("/")
def hello():
    """Main Flask function"""
    query = request.args.get("query")
    if query:

        sortcrit = request.args.get("sortcrit")
        if sortcrit:
            if sortcrit =="dateasc":
                sort = [{"date": {"order": "asc"}}]
            elif sortcrit == "datedesc":
                sort = [{"date": {"order": "desc"}}]
            elif sortcrit =="newspaper":
                sort = [{"journal": {"order": "asc"}}]
            else:
                sort = ["_score", {"date": {"order": "asc"}}]
        else:
            sortcrit = "relevance"
            sort = ["_score", {"date": {"order": "asc"}}]

        query_dic = {"bool": {"must": [{"query_string": {"query": query}}]}}
        query_dic["bool"]["filter"] = []
        query_dic["bool"]["should"] = []

        paper_list = request.args.getlist("paper")
        if paper_list:
            query_dic["bool"]["minimum_should_match"] = 1
            for paper in paper_list:
                query_dic["bool"]["should"].append({"match": {"journal": paper}})

        year_from = request.args.get("year_from")
        year_to = request.args.get("year_to")
        if year_from:
            query_dic["bool"]["must"].append({"range": {"year": {"gte": year_from,
                                                                 "lte": year_to}}})

        month_list = request.args.getlist("month")
        if month_list:
            query_dic["bool"]["minimum_should_match"] = 1
            for month in month_list:
                query_dic["bool"]["should"].append({"match": {"month": month}})

        day_from = request.args.get("day_from")
        day_to = request.args.get("day_to")
        if day_from:
            query_dic["bool"]["must"].append({"range": {"day": {"gte": day_from, "lte": day_to}}})

        dow_list = request.args.getlist("dow")
        if dow_list:
            query_dic["bool"]["minimum_should_match"] = 1
            for dow in dow_list:
                query_dic["bool"]["should"].append({"match": {"dow": dow}})

        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        if date_from or date_to:
            if not date_from:
                date_from = "1831-02-06"
            if not date_to:
                date_to = "1993-09-01"
            query_dic["bool"]["must"].append({"range": {"date": {"gte": date_from,
                                                                 "lte": date_to}}})

        edition = request.args.get("edition")
        if edition:
            query_dic["bool"]["filter"].append({"match": {"edition": edition}})

        page_from = request.args.get("page_from")
        page_to = request.args.get("page_to")
        if page_from:
            query_dic["bool"]["must"].append({"range": {"pagenb": {"gte": page_from,
                                                                   "lte": page_to}}})

        language = request.args.get("language")
        if language:
            query_dic["bool"]["filter"].append({"match": {"language": language}})

        endpoint = cred["endpoint"]
        es_url = f"{endpoint}/pages/_search"
        username = cred["username"]
        password = cred["password"]
        cert = cred["cert"]
        es = Elasticsearch(
            endpoint,
            ca_certs=cert,
            basic_auth=(username, password)
        )
        headers = {"Content-Type": "application/json; charset=utf8"}
        size = 10
        p = request.args.get("p")
        if p:
            p = int(p)
        else:
            p = 1
        fromp = (int(p)-1)*10

        highlight = {
            "fields": {
                "text": {}
            },
            "pre_tags": "<span class='serp__match'>",
            "post_tags": "</span>",
            "fragment_size": 500
        }

        resdic = es.search(index="pages", from_=fromp, size=size, sort=sort, track_total_hits=True, query=query_dic, highlight=highlight)        
        number = resdic["hits"]["total"]["value"]
        timing = f"{resdic['took']/1000:.2f}".replace('.', ',')
        if number == 0:
            found_string = "Aucun résultat"
        elif number == 1:
            found_string = "Un seul résultat"
        elif p == 1:
            nb = f"{number:,}".replace(',', ' ')
            found_string = f"{nb} résultats"
        else:
            nb = f"{number:,}".replace(',', ' ')
            found_string = f"Page {p} sur {nb} résultats"
        stats = f"{found_string} ({timing} secondes)"
        hits = resdic["hits"]
        results = []

        path = Path(__file__).parent / "static/newspapers.json"
        with open(path, encoding="utf-8") as f:
            names = json.load(f)
        all_papers = [{"code": code, "name": names[code]} for code in names]

        all_months = [{"code": f"{i:02d}",
                        "name": calendar.month_name[i]} for i in range(1, 13)]

        all_dows = [{"code": f"{i+1}", "name": calendar.day_name[i]} for i in range(7)]

        editions = [{"code": f"{i:02d}", "name": f"{i}e édition"} for i in range(1, 6)]
        editions += [{"code": i, "name": f"{i[1]}e édition spéciale"} for i in ["11", "12"]]
        if edition:
            matched_editions = [x for x in editions if x["code"] == edition]
        else:
            matched_editions = editions

        languages = [{"code": "fr-BE", "name": "français"}]
        if language:
            all_lang = [x for x in languages if x["code"] == language]
        else:
            all_lang = languages

        for hit in hits["hits"]:
            result_id = hit["_source"]["page"]
            np = hit["_source"]["journal"]
            name = names[np]
            hit_day = hit["_source"]["day"]
            hit_month = hit["_source"]["month"]
            hit_year = hit["_source"]["year"]
            page = int(hit["_source"]["pagenb"])
            display = f"{name} ({hit_day}/{hit_month}/{hit_year} - p. {page})"
            try:
                matches = hit["highlight"]["text"]
            except KeyError: # no matches (wildcard), defaulting to 500 first chars
                matches = [hit["_source"]["text"][:500] + "..."]
            all_matches = " [...] ".join(matches)
            all_matches = all_matches.replace("<span", "##!!##").replace("</span", "!!##!!")
            all_matches = all_matches.replace("<", "")
            all_matches = all_matches.replace("##!!##", "<span").replace("!!##!!", "</span")
            result = {"id": result_id, "display": display, "matches": all_matches}
            results.append(result)

        maxp = math.ceil(number/10)
        firstp = max(1, min(p-4, maxp-9))
        lastp = min(firstp+10, maxp+1)

        doc = request.args.get("doc")
        if doc:
            elements = doc.split("_")
            np = elements[1]
            if np == "15463334": # La Presse
                np = "B14138"
            doc_date = elements[2]
            doc_year = doc_date[:4]
            key = f"/mnt/data/PDF/{np}/{doc_year}/{doc}.pdf"
            return redirect(key)
        else:
            doc = "false"

        url = request.url
        if "&p=" in url:
            url = url.split("&p=")[0]
        url = url.replace("http://", "https://")

        ziparg = request.args.get("zip")
        if ziparg:
            query_norm = unidecode(query).replace(" ", "_")
            query_norm = "".join([c for c in query_norm if c.isalpha() or c == "_"])
            zippath = Path(__file__).parent / f"static/temp/camille_{query_norm}.zip"
            stats_journal = defaultdict(int)
            stats_year = defaultdict(int)
            with ZipFile(zippath, 'w') as myzip:
                total = min(number, 1000)
                print(f"Total: {total}")
                pages = 10 if total == 1000 else total // 100 + 1
                for i in range(pages):
                    resdic2 = es.search(index="pages", from_=i*100, size=100, sort=sort, query=query_dic)
                    hits2 = resdic2["hits"]
                    for hit in hits2["hits"]:
                        result_id = hit["_source"]["page"]
                        result_journal = hit["_source"]["journal"]
                        stats_journal[result_journal] += 1
                        result_year = str(hit["_source"]["year"])
                        stats_year[result_year] += 1
                        text = hit["_source"]["text"]
                        arcpath = f"{result_id}.txt"
                        abspath = Path(__file__).parent / f"static/temp/{arcpath}"
                        with open(abspath, "w", encoding="utf-8") as f:
                            f.write(text)
                        myzip.write(abspath, arcpath)
                        abspath.unlink()

                readme_path = Path(__file__).parent / "static/README.txt"
                new_readme_path = Path(__file__).parent / "static/temp/README.txt"
                copy(readme_path, new_readme_path)
                readme = open(new_readme_path, 'a', encoding="utf-8")
                readme.write("\n--- STATISTIQUES ---\n")
                readme.write(f"Nombre total de fichiers : {total}\n\n")
                for journal in sorted(stats_journal)[1:] + [sorted(stats_journal)[0]]:
                    readme.write(f"{journal} : {stats_journal[journal]}\n")
                readme.write("\n")
                for year in sorted(stats_year):
                    readme.write(f"{year} : {stats_year[year]}\n")
                readme.close()
                myzip.write(new_readme_path, "_README.txt")
            return send_file(zippath, as_attachment=True)

        xlsx = request.args.get("xlsx")
        if xlsx:
            total = min(number, 25000)
            pages_xlsx = 25 if total == 25000 else total // 1000 + 1
            query_norm = unidecode(query).replace(" ", "_")
            query_norm = "".join([c for c in query_norm if c.isalpha() or c == "_"])
            xlsxpath = Path(__file__).parent / f"static/temp/camille_{query_norm}.xlsx"
            df = pd.DataFrame([], columns=['ID', 'JOURNAL', 'DATE', 'ANNÉE', 'MOIS', 'JOUR',
                                            'JDLS', 'ÉDITION', 'PAGE', 'LANGUE', 'TEXTE'])
            for i in range(pages_xlsx):
                highlight = {
                    "fields": {
                        "text": {}
                    },
                    "pre_tags": "<kw>",
                    "post_tags": "</kw>",
                    "fragment_size": 2000
                }

                resdic2 = es.search(index="pages", from_=i*1000, size=1000, sort=sort, query=query_dic, highlight=highlight)
                hits2 = resdic2["hits"]
                for hit in hits2["hits"]:
                    result_id = hit["_source"]["page"]
                    journal = hit["_source"]["journal"]
                    date = hit["_source"]["date"]
                    year = hit["_source"]["year"]
                    month = hit["_source"]["month"]
                    day = hit["_source"]["day"]
                    dow = hit["_source"]["dow"]
                    edition = hit["_source"]["edition"]
                    pagenb = hit["_source"]["pagenb"]
                    language = hit["_source"]["language"]
                    try:
                        matches = hit["highlight"]["text"]
                    except KeyError: # no matches (wildcard), defaulting to 2000 first chars
                        matches = [hit["_source"]["text"][:2000] + "..."]
                    text = " [...] ".join(matches)
                    line = [result_id, journal, date, year, month, day,
                            dow, edition, pagenb, language, text]
                    try:
                        series = pd.Series(line, index=df.columns.tolist()[:11])
                    except ValueError: # mismatch between index and data
                        print(df.columns)
                        sys.exit()
                    df = pd.concat([df, series], ignore_index=True)

            df['DATE'] = pd.to_datetime(df['DATE']).dt.date
            print(df)
            df = df.astype({'ANNÉE': 'int32', 'MOIS': 'int32', 'JOUR': 'int32',
                                'JDLS': 'int32', 'ÉDITION': 'int32', 'PAGE': 'int32'})
            df.to_excel(xlsxpath, index=None)
            return send_file(xlsxpath, as_attachment=True)

        html = render_template("results.html", query=query, stats=stats,
                                results=results, p=p, firstp=firstp, lastp=lastp,
                                maxp=maxp, doc=doc, url=url, all_papers=all_papers,
                                number=number, sortcrit=sortcrit, paper_list=paper_list,
                                year_from=year_from, year_to=year_to, all_months=all_months,
                                month_list=month_list, all_dows=all_dows, dow_list=dow_list,
                                editions=matched_editions, edition=edition, languages=all_lang,
                                language=language, page_from=page_from, page_to=page_to,
                                day_from=day_from, day_to=day_to, date_from=date_from,
                                date_to=date_to
                                )

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
