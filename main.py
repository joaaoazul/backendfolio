from flask import Flask, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

projects_list = [
    {
        "title": "Portefólio Flask + HTMX",
        "desc": "Desenvolvimento de uma SPA focada em performance.",
        "tech": ["Python", "Flask", "HTMX", "Tailwind"],
        "link": "https://github.com/joaaoazul/portfoliojo"
    },
]

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/projects")
def get_projects():
    return jsonify(projects_list)

if __name__ == "__main__":
    app.run(debug=True, port=8000)