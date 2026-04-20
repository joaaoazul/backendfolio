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
    {
        "title": "Hotel JMV",
        "desc": "Aplicação Full-Stack para gestão hoteleira, com funcionalidades de reservas, check-in/out e gestão de quartos.",
        "tech": ["Python", "Flask", "HTML", "MySQL"],
        "link": "https://github.com/joaaoazul/Hotel-JMV.git"
    },
    {
        "title": "Rickys Chinaware",
        "desc": "Aplicação de solução em Java para gestão de inventário para uma loja de porcelanas, permitindo o acompanhamento de stock, vendas e clientes.",
        "tech": ["Java"],
        "link": "https://github.com/joaaoazul/tp1-loja.virtual.git"
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