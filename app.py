from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home-content")
def home_content():
    return render_template("home_fragment.html")

@app.route("/get-video")
def get_video():
    return '''
            <video autoplay muted loop playsinline class="absolute inset-0 w-full h-full object-cover opacity-100 transition-opacity duration-500 z-0">
                <source src="/static/assets/joaolive.MOV" type="video/mp4">
            </video>
        '''


projects_list = [

    {
        "title": "Portefólio Flask + HTMX",
        "desc": "Desenvolvimento de uma SPA (Single Page Application) focada em performance.",
        "tech": ["Python", "Flask", "HTMX", "Tailwind"],
        "link": "https://github.com/joaaoazul/portfoliojo"
    },

]

@app.route("/projects-content")
def projects_content():
    return render_template("projects_fragment.html", projects=projects_list)

if __name__ == "__main__":
    app.run(debug=True)