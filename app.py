import os
from flask import Flask, render_template, session, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "chave_secreta_portfolio"

TRANSLATIONS = {
    "pt": {
        "projetos": "Projetos",
        "sobre": "Sobre",
        "estudante": "Estudante e",
        "futuro": "Futuro",
        "engenheiro": "Engenheiro",
        "de_software": "<br>de Software.",
        "desc": "Focado em Python e infraestrutura. Aluno da UAlg, a explorar DevOps e CyberSec.",
        "btn_projetos": "Explorar Projetos",
        "btn_cv": "Download Curriculum",
        "btn_repo": "Explorar Repositório",
        "p_titulo": "Portefólio Flask + HTMX",
        "p_desc": "Desenvolvimento de uma SPA (Single Page Application) focada em performance.",
        "footer": "Feito em Faro, Portugal 🇵🇹",
        "construir": "Vamos construir <br>algo <span class=\"text-techgreen\">juntos?</span>",
        "btn_contacto": "Entra em contacto!",
        "tecnologias": "Tecnologias"
    },
    "en": {
        "projetos": "Projects",
        "sobre": "About",
        "estudante": "Student and",
        "futuro": "Future Software",
        "engenheiro": "Engineer.",
        "de_software": "",
        "desc": "Focused on Python and infrastructure. UAlg student, exploring DevOps and CyberSec.",
        "btn_projetos": "Explore Projects",
        "btn_cv": "Download Resume",
        "btn_repo": "Explore Repository",
        "p_titulo": "Flask + HTMX Portfolio",
        "p_desc": "Development of a performance-focused SPA (Single Page Application).",
        "footer": "Made in Faro, Portugal 🇵🇹",
        "construir": "Shall we build <br>something <span class=\"text-techgreen\">together?</span>",
        "btn_contacto": "Get in touch!",
        "tecnologias": "Technologies"
    }
}

@app.context_processor
def inject_translations():
    lang = session.get("language", "pt")
    return dict(t=TRANSLATIONS.get(lang, TRANSLATIONS["pt"]))

@app.route("/language/<language>")
def set_language(language):
    if language in ["pt", "en"]:
        session["language"] = language
        session.modified = True
    return redirect(request.referrer or url_for('index'))

@app.route("/")
def index():
    return render_template("index.html", active_page='home')

@app.route("/home-content")
def home_content():
    if 'HX-Request' in request.headers:
        return render_template("home_fragment.html")
    return redirect(url_for('index'))

@app.route("/projects-content")
def projects_content():
    lang = session.get("language", "pt")

    projects_list = [
        {
            "title": TRANSLATIONS[lang]["p_titulo"],
            "desc": TRANSLATIONS[lang]["p_desc"],
            "tech": ["Python", "Flask", "HTMX", "Tailwind"],
            "link": "https://github.com/joaaoazul/portfoliojo"
        },
    ]

    if 'HX-Request' in request.headers:
        return render_template("projects_fragment.html", projects=projects_list)

    return render_template("index.html", active_page='projects', projects=projects_list)

if __name__ == "__main__":
    app.run(debug=True)