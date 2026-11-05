from livereload import Server
from app import app

app.config["TEMPLATES_AUTO_RELOAD"] = True

server = Server(app.wsgi_app)

server.watch("app.py")
server.watch("templates/")
server.watch("static/")

server.serve(port=5500, debug=True)