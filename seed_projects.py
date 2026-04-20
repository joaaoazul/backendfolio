from app import app, db, Projeto

projects = [
    {
        "title_pt": "Portefólio Pessoal",
        "title_en": "Personal Portfolio",
        "desc_pt": "Desenvolvimento de uma SPA (Single Page Application) focada em performance.",
        "desc_en": "Development of a performance-focused SPA (Single Page Application).",
        "tech": "Python,Flask,HTMX,Tailwind",
        "link": "https://github.com/joaaoazul/portfoliojo"
    },
    {
        "title_pt": "Hotel JMV",
        "title_en": "Hotel JMV",
        "desc_pt": "Aplicação Full-Stack para gestão hoteleira, com funcionalidades de reservas, check-in/out e gestão de quartos.",
        "desc_en": "Full-Stack application for hotel management, with reservation, check-in/out and room management features.",
        "tech": "Python,Flask,HTML,MySQL",
        "link": "https://github.com/joaaoazul/Hotel-JMV.git"
    },
    {
        "title_pt": "Ricky's Chinaware",
        "title_en": "Ricky's Chinaware",
        "desc_pt": "Aplicação de solução em Java para gestão de inventário para uma loja de porcelanas, permitindo o acompanhamento de stock, vendas e clientes.",
        "desc_en": "Java-based inventory management application for a porcelain store, enabling stock tracking, sales and customer management.",
        "tech": "Java",
        "link": "https://github.com/joaaoazul/tp1-loja.virtual.git"
    }
]

with app.app_context():
    for p in projects:
        proj = Projeto(
            title_pt=p['title_pt'],
            title_en=p['title_en'],
            desc_pt=p['desc_pt'],
            desc_en=p['desc_en'],
            tech=p['tech'],
            link=p['link']
        )
        db.session.add(proj)
    db.session.commit()
    print(f"Inseridos {len(projects)} projetos.")
