import os
from babel.messages.pofile import read_po
from babel.messages.mofile import write_mo

os.makedirs('translations/en/LC_MESSAGES', exist_ok=True)

po_content = """msgid ""
msgstr ""
"Project-Id-Version: 1.0\\n"
"Content-Type: text/plain; charset=utf-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Language: en\\n"

msgid "Projetos"
msgstr "Projects"

msgid "Sobre"
msgstr "About"

msgid "Estudante e"
msgstr "Student and"

msgid "Futuro"
msgstr "Future Software"

msgid "Engenheiro"
msgstr "Engineer."

msgid "<br>de Software."
msgstr ""

msgid "Focado em Python e infraestrutura. Aluno da UAlg, a explorar DevOps e CyberSec."
msgstr "Focused on Python and infrastructure. UAlg student, exploring DevOps and CyberSec."

msgid "Explorar Projetos"
msgstr "Explore Projects"

msgid "Download Curriculum"
msgstr "Download Resume"

msgid "Explorar Repositório"
msgstr "Explore Repository"

msgid "Vamos construir <br>algo <span class=\\"text-techgreen\\">juntos?</span>"
msgstr "Shall we build <br>something <span class=\\"text-techgreen\\">together?</span>"

msgid "Entra em contacto!"
msgstr "Get in touch!"

msgid "Tecnologias"
msgstr "Technologies"

msgid "Portefólio Flask + HTMX"
msgstr "Flask + HTMX Portfolio"

msgid "Desenvolvimento de uma SPA (Single Page Application) focada em performance."
msgstr "Development of a performance-focused SPA (Single Page Application)."

msgid "João Azul | Portfólio"
msgstr "João Azul | Portfolio"

msgid "Feito em Faro, Portugal 🇵🇹"
msgstr "Made in Faro, Portugal 🇵🇹"
"""

po_path = 'translations/en/LC_MESSAGES/messages.po'
mo_path = 'translations/en/LC_MESSAGES/messages.mo'

with open(po_path, 'w', encoding='utf-8') as f:
    f.write(po_content)

with open(po_path, 'rb') as f_in:
    catalog = read_po(f_in)

with open(mo_path, 'wb') as f_out:
    write_mo(f_out, catalog)

print("✅ Tradução atualizada e compilada com sucesso!")