from flask import Flask, render_template
from auth import auth_page

app = Flask(__name__)
app.config['SECRET_KEY'] = 'such a secret wow'
app.register_blueprint(auth_page)

@app.route('/')
def index():
    return render_template("index.html")
