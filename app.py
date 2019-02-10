from flask import Flask
from auth import auth_page

app = Flask(__name__)
app.register_blueprint(auth_page)

@app.route('/')
def index():
    return "Hello Azure!"
