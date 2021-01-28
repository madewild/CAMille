"""Basis Flask app"""

from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello():
    return "<h1>CAMILLE</h1><h2>Centre d'Archives sur les Médias et l'Information"
if __name__ == "__main__":
    app.run()
