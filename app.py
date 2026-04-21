import os
import json
import requests
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, session, request, redirect, url_for, flash, jsonify
from sqlalchemy.exc import SQLAlchemyError
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contactos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

BASEDIR = os.path.abspath(os.path.dirname(__file__))

csrf = CSRFProtect(app)
db = SQLAlchemy(app)


class Contacto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lido = db.Column(db.Boolean, default=False)


class Projeto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_pt = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=True)
    desc_pt = db.Column(db.Text, nullable=False)
    desc_en = db.Column(db.Text, nullable=True)
    tech = db.Column(db.String(300), nullable=False, default='')
    link = db.Column(db.String(300), nullable=True)

    @property
    def tech_list(self):
        return [t.strip() for t in self.tech.split(',') if t.strip()]

    def to_dict(self, lang='pt'):
        return {
            'id': self.id,
            'title_pt': self.title_pt,
            'title_en': self.title_en or self.title_pt,
            'desc_pt': self.desc_pt,
            'desc_en': self.desc_en or self.desc_pt,
            'title': self.title_en if lang == 'en' and self.title_en else self.title_pt,
            'desc': self.desc_en if lang == 'en' and self.desc_en else self.desc_pt,
            'tech': self.tech_list,
            'link': self.link or ''
        }


class Certificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    issuer = db.Column(db.String(200), nullable=False)
    icon = db.Column(db.String(30), nullable=False, default='shield')
    order_index = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'issuer': self.issuer,
            'icon': self.icon,
            'order_index': self.order_index,
        }


DEFAULT_CERTIFICATIONS = [
    {'title': 'Introduction to Cybersecurity', 'issuer': 'Cisco Networking Academy', 'icon': 'shield'},
    {'title': 'Networking Basics', 'issuer': 'Cisco Networking Academy', 'icon': 'shield'},
    {'title': 'Endpoint Security', 'issuer': 'Cisco Networking Academy', 'icon': 'shield'},
    {'title': 'Network Defense', 'issuer': 'Cisco Networking Academy', 'icon': 'shield'},
    {'title': 'Cyber Threat Management', 'issuer': 'Cisco Networking Academy', 'icon': 'shield'},
    {'title': 'Ethical Hacker', 'issuer': 'Cisco Networking Academy', 'icon': 'lock'},
    {'title': 'Boas Práticas de Cibersegurança', 'issuer': 'CNCS - Centro Nacional de Ciberseguranca', 'icon': 'lock'},
    {'title': 'Fundamentos de Cibersegurança', 'issuer': 'CNCS - Centro Nacional de Ciberseguranca', 'icon': 'lock'},
    {'title': 'Resiliência de Cibersegurança', 'issuer': 'CNCS - Centro Nacional de Ciberseguranca', 'icon': 'lock'},
]


with app.app_context():
    db.create_all()
    if Certificacao.query.count() == 0:
        for idx, cert in enumerate(DEFAULT_CERTIFICATIONS):
            db.session.add(Certificacao(
                title=cert['title'],
                issuer=cert['issuer'],
                icon=cert['icon'],
                order_index=idx
            ))
        db.session.commit()


def load_translations():
    translations = {}
    for lang in ['pt', 'en']:
        path = os.path.join(BASEDIR, 'translations', f'{lang}.json')
        with open(path, encoding='utf-8') as f:
            translations[lang] = json.load(f)
    return translations

TRANSLATIONS = load_translations()

VALIDATION_ERROR_MAP = {
    'pt': {
        'This field is required.': 'Este campo é obrigatório.',
        'Invalid email address.': 'Email inválido.',
        'Field must be at least 2 characters long.': 'O campo deve ter pelo menos 2 caracteres.',
        'Field must be at least 10 characters long.': 'O campo deve ter pelo menos 10 caracteres.',
    },
    'en': {
        'This field is required.': 'This field is required.',
        'Invalid email address.': 'Invalid email address.',
        'Field must be at least 2 characters long.': 'This field must contain at least 2 characters.',
        'Field must be at least 10 characters long.': 'This field must contain at least 10 characters.',
    }
}


def localize_form_error(error_text: str) -> str:
    lang = session.get('language', 'pt')
    lang_map = VALIDATION_ERROR_MAP.get(lang, VALIDATION_ERROR_MAP['pt'])
    return lang_map.get(error_text, error_text)


@app.context_processor
def inject_translations():
    lang = session.get('language', 'pt')
    merged = {**TRANSLATIONS['pt'], **TRANSLATIONS.get(lang, {})}
    return dict(t=merged, localize_error=localize_form_error)


def send_telegram(name: str, email: str, message: str) -> bool:
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        app.logger.warning("Telegram nao configurado.")
        return False
    text = (
        "📬 *Novo contacto no portefólio*\n\n"
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


@app.route("/language/<language>")
def set_language(language):
    if language in ["pt", "en"]:
        session["language"] = language
        session.modified = True

    # Keep users on the current in-site page after switching language.
    next_url = request.args.get("next", "")
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        return redirect(next_url)

    return redirect(request.referrer or url_for('index'))


class ContactForm(FlaskForm):
    name = StringField(validators=[DataRequired(), Length(min=2)])
    email = StringField(validators=[DataRequired(), Email()])
    message = TextAreaField(validators=[DataRequired(), Length(min=10)])
    submit = SubmitField()


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    lang = session.get('language', 'pt')
    form = ContactForm()
    error_msg = TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get('error_msg', 'Erro ao enviar.')
    flash(error_msg)
    if "HX-Request" in request.headers:
        return render_template("contacts_fragment.html", form=form), 400
    return render_template("index.html", active_page="contact", form=form), 400


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/admin/login", methods=["GET", "POST"])
@csrf.exempt
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


@app.route('/admin/api/projects', methods=['GET'])
@csrf.exempt
@admin_required
def api_projects_list():
    projetos = Projeto.query.order_by(Projeto.id).all()
    return jsonify([p.to_dict('pt') for p in projetos])


@app.route("/admin/api/projects", methods=["POST"])
@csrf.exempt
@admin_required
def api_projects_create():
    data = request.get_json()
    if not data or not data.get("title_pt") or not data.get("desc_pt"):
        return jsonify({"error": "Dados invalidos"}), 400
    p = Projeto(
        title_pt=data["title_pt"].strip(),
        title_en=data.get("title_en", "").strip() or None,
        desc_pt=data["desc_pt"].strip(),
        desc_en=data.get("desc_en", "").strip() or None,
        tech=data.get("tech", "").strip(),
        link=data.get("link", "").strip() or None,
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201


@app.route("/admin/api/projects/<int:id>", methods=["PUT"])
@csrf.exempt
@admin_required
def api_projects_update(id):
    p = Projeto.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados invalidos"}), 400
    p.title_pt = data.get("title_pt", p.title_pt).strip()
    p.title_en = data.get("title_en", p.title_en or "").strip() or None
    p.desc_pt = data.get("desc_pt", p.desc_pt).strip()
    p.desc_en = data.get("desc_en", p.desc_en or "").strip() or None
    p.tech = data.get("tech", p.tech).strip()
    p.link = data.get("link", p.link or "").strip() or None
    db.session.commit()
    return jsonify(p.to_dict())


@app.route("/admin/api/projects/<int:id>", methods=["DELETE"])
@csrf.exempt
@admin_required
def api_projects_delete(id):
    p = Projeto.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"ok": True})


@app.route('/admin/api/certifications', methods=['GET'])
@csrf.exempt
@admin_required
def api_certifications_list():
    certs = Certificacao.query.order_by(Certificacao.order_index.asc(), Certificacao.id.asc()).all()
    return jsonify([c.to_dict() for c in certs])


@app.route('/admin/api/certifications', methods=['POST'])
@csrf.exempt
@admin_required
def api_certifications_create():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('issuer'):
        return jsonify({'error': 'Dados invalidos'}), 400

    max_order = db.session.query(db.func.max(Certificacao.order_index)).scalar()
    next_order = (max_order + 1) if max_order is not None else 0

    cert = Certificacao(
        title=data['title'].strip(),
        issuer=data['issuer'].strip(),
        icon=(data.get('icon') or 'shield').strip(),
        order_index=next_order,
    )
    db.session.add(cert)
    db.session.commit()
    return jsonify(cert.to_dict()), 201


@app.route('/admin/api/certifications/<int:id>', methods=['PUT'])
@csrf.exempt
@admin_required
def api_certifications_update(id):
    cert = Certificacao.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados invalidos'}), 400

    cert.title = data.get('title', cert.title).strip()
    cert.issuer = data.get('issuer', cert.issuer).strip()
    cert.icon = data.get('icon', cert.icon).strip() or cert.icon
    if 'order_index' in data:
        try:
            cert.order_index = int(data['order_index'])
        except (TypeError, ValueError):
            pass

    db.session.commit()
    return jsonify(cert.to_dict())


@app.route('/admin/api/certifications/<int:id>', methods=['DELETE'])
@csrf.exempt
@admin_required
def api_certifications_delete(id):
    cert = Certificacao.query.get_or_404(id)
    db.session.delete(cert)
    db.session.commit()
    return jsonify({'ok': True})


@app.route("/")
def index():
    return render_template("index.html", active_page='home', form=ContactForm())


@app.route("/contact-content")
def contact_content():
    form = ContactForm()
    if "HX-Request" in request.headers:
        return render_template("contacts_fragment.html", form=form)
    return render_template("index.html", active_page="contact", form=form)


@app.route("/contact", methods=["POST"])
def contact_submit():
    form = ContactForm()
    lang = session.get("language", "pt")

    if form.validate_on_submit():
        try:
            contacto = Contacto(
                name=form.name.data,
                email=form.email.data,
                message=form.message.data
            )
            db.session.add(contacto)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Erro ao guardar contacto: {e}")
            error_msg = TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get('error_msg', 'Erro ao enviar contacto.')
            flash(error_msg)
            if "HX-Request" in request.headers:
                return render_template("contacts_fragment.html", form=form)
            return render_template("index.html", active_page="contact", form=form)

        send_telegram(form.name.data, form.email.data, form.message.data)
        msg = TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get('success_msg', '')
        if "HX-Request" in request.headers:
            return render_template("contacts_fragment.html", form=ContactForm(), success=True, msg=msg)
        flash(msg)
        return redirect(url_for("contact_content"))

    else:
        field_label_map = {
            'name': TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get('name_label', 'Name').replace('*', '').strip(),
            'email': TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get('email_label', 'Email').replace('*', '').strip(),
            'message': TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get('message_label', 'Message').replace('*', '').strip(),
        }
        validation_prefix = TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get('validation_prefix', 'Erro')
        for field, errors in form.errors.items():
            for error in errors:
                translated_error = localize_form_error(error)
                field_label = field_label_map.get(field, field)
                flash(f"{validation_prefix} ({field_label}): {translated_error}")
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
    lang = session.get('language', 'pt')
    projetos = Projeto.query.order_by(Projeto.id).all()
    projects_list = [p.to_dict(lang) for p in projetos]
    if "HX-Request" in request.headers:
        return render_template("projects_fragment.html", projects=projects_list)
    return render_template("index.html", active_page="projects", projects=projects_list, form=ContactForm())


@app.route("/about-content")
def about_content():
    certifications = Certificacao.query.order_by(Certificacao.order_index.asc(), Certificacao.id.asc()).all()
    if "HX-Request" in request.headers:
        return render_template("about_fragment.html", certifications=certifications)
    return render_template("index.html", active_page="about", form=ContactForm(), certifications=certifications)


@app.route("/privacy")
def privacy_page():
    return render_template("privacy.html")


@app.route("/cookies")
def cookies_page():
    return render_template("cookies.html")


if __name__ == "__main__":
    app.run(debug=True)
