import os
from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

from dotenv import load_dotenv

load_dotenv()

import resend

resend.api_key = os.environ.get("RESEND_API_KEY")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "joaoazul@gmail.com")

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
        "desc": "Desenvolvimento Front-End, Back-End e Redes, com uma veia de Cibersegurança. Estudante na UAlg.",
        "btn_projetos": "Explorar Projetos",
        "btn_cv": "Download Curriculum",
        "btn_repo": "Explorar Repositório",
        "p_titulo": "Portefólio Flask + HTMX",
        "p_desc": "Desenvolvimento de uma SPA (Single Page Application) focada em performance.",
        "footer": "Feito em Faro, Portugal 🇵🇹",
        "construir": "Vamos construir <br>algo <span class=\"text-techgreen\">juntos?</span>",
        "btn_contacto": "Entra em contacto!",
        "tecnologias": "Tecnologias",
        "contact_title": "Contacto",
        "name_label": "Nome *",
        "email_label": "Email *",
        "message_label": "Mensagem *",
        "submit_label": "Enviar Mensagem",
        "success_msg": "Comunicação estabelecida! Recebi a tua mensagem e respondo em breve.",
        "error_msg": "Falha na ligação externa. Verifica os dados e tenta novamente."
    },
    "en": {
        "projetos": "Projects",
        "sobre": "About",
        "estudante": "Student and",
        "futuro": "Future Software",
        "engenheiro": "Engineer.",
        "de_software": "",
        "desc": "Front-End, Back-End, and Network development, with a cybersecurity vein. UAlg student.",
        "btn_projetos": "Explore Projects",
        "btn_cv": "Download Resume",
        "btn_repo": "Explore Repository",
        "p_titulo": "Flask + HTMX Portfolio",
        "p_desc": "Development of a performance-focused SPA (Single Page Application).",
        "footer": "Made in Faro, Portugal 🇵🇹",
        "construir": "Shall we build <br>something <span class=\"text-techgreen\">together?</span>",
        "btn_contacto": "Get in touch!",
        "tecnologias": "Technologies",
        "contact_title": "Contacto",
        "name_label": "Nome *",
        "email_label": "Email *",
        "message_label": "Mensagem *",
        "submit_label": "Enviar Mensagem",
        "success_msg": "Communication established! I received your message and will reply soon.",
        "error_msg": "External connection failed. Check your data and try again."
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


class ContactForm(FlaskForm):
    name = StringField(validators=[DataRequired(), Length(min=2)])
    email = StringField(validators=[DataRequired(), Email()])
    message = TextAreaField(validators=[DataRequired(), Length(min=10)])
    submit = SubmitField()


@app.route("/")
def index():
    form = ContactForm()
    return render_template("index.html", active_page='home', form=form)


@app.route("/contact", methods=['GET', 'POST'])
@app.route("/contact-content")
def contact():
    form = ContactForm()
    lang = session.get("language", "pt")

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                params = {
                    "from": "contact@joaoazul.dev",
                    "to": [ADMIN_EMAIL],
                    "reply_to": form.email.data,
                    "subject": f"Contacto: {form.name.data}",
                    "html": f"<h2>Contacto Novo</h2><p><b>{form.name.data}</b> ({form.email.data})<br>{form.message.data}</p>"
                }
                resend.Emails.send(params)


                if 'HX-Request' in request.headers:
                    return render_template("contacts_fragment.html", form=form, success=True,
                                           msg=TRANSLATIONS[lang]["success_msg"])

                flash(TRANSLATIONS[lang]["success_msg"])
            except Exception as e:
                print(f"\n[ERRO RESEND]: {e}\n")
                flash(TRANSLATIONS[lang]["error_msg"])
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Falha ({field}): {error}")

        if 'HX-Request' in request.headers:
            return render_template("contacts_fragment.html", form=form)
        return redirect(url_for('contact'))

    if 'HX-Request' in request.headers:
        return render_template("contacts_fragment.html", form=form)

    return render_template("index.html", active_page='contact', form=form)


@app.route("/home-content")
def home_content():
    form = ContactForm()
    if 'HX-Request' in request.headers:
        return render_template("home_fragment.html", form=form)
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