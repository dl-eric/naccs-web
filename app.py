from flask import Flask, render_template, session
from auth import auth_page
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.register_blueprint(auth_page)

@app.route('/')
def index():
    return render_template("index.html", username=session.get('username'))

if __name__ == '__main__':
    if os.environ.get('FLASK_DEBUG'):
        app.run(debug=True)
    else:
        app.run()