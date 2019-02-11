from flask import Flask, render_template
from auth import auth_page
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.register_blueprint(auth_page)

@app.route('/')
def index():
    return render_template("index.html")
