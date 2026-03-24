import os
import requests
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contactos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Contacto(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), nullable=False)
    message    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lido       = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()


def send_telegram(name: str, email: str, message: str) -> bool:
    token   = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        app.logger.warning("Telegram não configurado.")
        return False

    text = (
        f"📬 *Novo contacto no portefólio*\n\n"
        f"👤 *Nome:* {name}\n"
        f"✉️ *Email:* `{email}`\n"
        f"🕐 *Data:* {datetime.utcnow():%d/%m/%Y %H:%M} UTC\n\n"
        f"💬 *Mensagem:*\n{message}"
    )

    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=5
        )
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        app.logger.error(f"Erro Telegram: {e}")
        return False


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
        "error_msg": "Algo correu mal. Tenta novamente.",
        "about_title": "Sobre",
        "about_greeting": "Olá, sou o João",
        "about_p1": "Estudante de <span class=\"text-white font-bold\">Tecnologias Informáticas</span> na Universidade do Algarve, com foco em desenvolvimento de software, redes e cibersegurança. A minha stack técnica inclui <span class=\"text-white font-bold\">Python, Java, JavaScript e React</span>, aliada a conhecimentos práticos em Linux e infraestrutura de redes.",
        "about_p2": "Paralelamente ao percurso académico, sirvo na <span class=\"text-white font-bold\">Guarda Nacional Republicana</span> — experiência que moldou a minha disciplina, trabalho em equipa e capacidade de resposta sob pressão.",
        "about_p3": "Tenho formação especializada em <span class=\"text-white font-bold\">cibersegurança ofensiva, resposta a incidentes e ciberresiliência</span>. Valorizo a eficiência, a melhoria contínua e a construção de soluções que funcionam mesmo quando o ambiente não coopera.",
        "about_based": "Based in",
        "about_years": "Anos a programar",
        "about_certs": "CyberSec & Dev",
        "about_percurso": "Percurso",
        "about_certificacoes": "Certificações",
        "about_cta": "Tens um projecto em mente ou queres trocar ideias?",
        "exp_gnr_title": "Guarda · Patrulheiro",
        "exp_gnr_org": "Guarda Nacional Republicana",
        "exp_gnr_date": "mar 2023 — presente",
        "exp_gnr_desc": "Serviço operacional de patrulha às ocorrências, atendimento ao público, ao encontro das competências de trabalho em equipa, gestão de situações de pressão e stress, mediação e resolução de conflitos, adaptabilidade a ambientes dinâmicos e imprevisíveis, entre outras competências.",
        "exp_ualg_title": "CTEsP em Tecnologias Informáticas",
        "exp_ualg_org": "Universidade do Algarve",
        "exp_ualg_date": "set 2025 — jun 2027",
        "exp_gnr_curso_title": "Curso de Formação de Guardas",
        "exp_gnr_curso_org": "Escola da GNR — Portalegre",
        "exp_gnr_curso_date": "jun 2022 — mar 2023",
        "exp_sec_title": "Línguas e Humanidades",
        "exp_sec_org": "ES de Vila Real de Santo António",
        "exp_sec_date": "2008 — 2021",
        "badge_atual": "Atual",
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
        "contact_title": "Contact",
        "name_label": "Name *",
        "email_label": "Email *",
        "message_label": "Message *",
        "submit_label": "Send Message",
        "success_msg": "Communication established! I received your message and will reply soon.",
        "error_msg": "Something went wrong. Please try again.",
        "about_title": "About",
        "about_greeting": "Hi, I'm João",
        "about_p1": "Student of <span class=\"text-white font-bold\">Information Technologies</span> at the University of Algarve, focused on software development, networking and cybersecurity. My tech stack includes <span class=\"text-white font-bold\">Python, Java, JavaScript and React</span>, combined with hands-on knowledge in Linux and network infrastructure.",
        "about_p2": "Alongside my academic path, I serve in the <span class=\"text-white font-bold\">GNR (National Republican Guard)</span> — an experience that shaped my discipline, teamwork and ability to perform under pressure.",
        "about_p3": "I have specialized training in <span class=\"text-white font-bold\">offensive cybersecurity, incident response and cyber resilience</span>. I value efficiency, continuous improvement and building solutions that work even when the environment doesn't cooperate.",
        "about_based": "Based in",
        "about_years": "Years coding",
        "about_certs": "CyberSec & Dev",
        "about_percurso": "Experience",
        "about_certificacoes": "Certifications",
        "about_cta": "Have a project in mind or want to exchange ideas?",
        "exp_gnr_title": "Guard · Patrol Officer",
        "exp_gnr_org": "National Republican Guard",
        "exp_gnr_date": "Mar 2023 — present",
        "exp_gnr_desc": "Operational patrol service, public assistance — developing teamwork, stress management, conflict mediation, and adaptability to dynamic and unpredictable environments.",
        "exp_ualg_title": "CTEsP in Information Technologies",
        "exp_ualg_org": "University of Algarve",
        "exp_ualg_date": "Sep 2025 — Jun 2027",
        "exp_gnr_curso_title": "Guard Training Course",
        "exp_gnr_curso_org": "GNR School — Portalegre",
        "exp_gnr_curso_date": "Jun 2022 — Mar 2023",
        "exp_sec_title": "Languages and Humanities",
        "exp_sec_org": "ES de Vila Real de Santo António",
        "exp_sec_date": "2008 — 2021",
        "badge_atual": "Current",
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
    name    = StringField(validators=[DataRequired(), Length(min=2)])
    email   = StringField(validators=[DataRequired(), Email()])
    message = TextAreaField(validators=[DataRequired(), Length(min=10)])
    submit  = SubmitField()


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == os.environ.get("ADMIN_PASSWORD"):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        error = "Password incorreta."
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    contactos = Contacto.query.order_by(Contacto.created_at.desc()).all()
    Contacto.query.filter_by(lido=False).update({"lido": True})
    db.session.commit()
    return render_template("admin_dashboard.html", contactos=contactos)


@app.route("/admin/delete/<int:id>", methods=["POST"])
@admin_required
def admin_delete(id):
    contacto = Contacto.query.get_or_404(id)
    db.session.delete(contacto)
    db.session.commit()
    return redirect(url_for("admin_dashboard"))


@app.route("/")
def index():
    return render_template("index.html", active_page='home', form=ContactForm())


@app.route("/contact", methods=["GET", "POST"])
@app.route("/contact-content")
def contact():
    form = ContactForm()
    lang = session.get("language", "pt")

    if request.method == "POST" and form.validate_on_submit():
        contacto = Contacto(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        db.session.add(contacto)
        db.session.commit()

        send_telegram(form.name.data, form.email.data, form.message.data)

        if "HX-Request" in request.headers:
            return render_template("contacts_fragment.html", form=form,
                                   success=True, msg=TRANSLATIONS[lang]["success_msg"])
        flash(TRANSLATIONS[lang]["success_msg"])
        return redirect(url_for("contact"))

    elif request.method == "POST":
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro ({field}): {error}")

    if "HX-Request" in request.headers:
        return render_template("contacts_fragment.html", form=form)
    return render_template("index.html", active_page="contact", form=form)


@app.route("/home-content")
def home_content():
    if "HX-Request" in request.headers:
        return render_template("home_fragment.html", form=ContactForm())
    return redirect(url_for("index"))


@app.route("/projects-content")
def projects_content():
    lang = session.get("language", "pt")
    projects_list = [{
        "title": TRANSLATIONS[lang]["p_titulo"],
        "desc":  TRANSLATIONS[lang]["p_desc"],
        "tech":  ["Python", "Flask", "HTMX", "Tailwind"],
        "link":  "https://github.com/joaaoazul/portfoliojo"
    }]
    if "HX-Request" in request.headers:
        return render_template("projects_fragment.html", projects=projects_list)
    return render_template("index.html", active_page="projects", projects=projects_list)


@app.route("/about-content")
def about_content():
    if "HX-Request" in request.headers:
        return render_template("about_fragment.html")
    return render_template("index.html", active_page="about")


if __name__ == "__main__":
    app.run(debug=True)