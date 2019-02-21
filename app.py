from flask import Flask, render_template, session, request
from auth import auth_page
import os
from matches import Matches

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.register_blueprint(auth_page)

@app.route('/')
def index():
    headers = {
        "User-Agent": request.headers.get('User-Agent'),
        "Referer": request.url
    }
    print(headers)

    scraper = Matches(headers)

    try:
        matches = scraper.get_matches()
    except:
        matches = {}
    
    return render_template("index.html", username=session.get('username'), matches=matches)

if __name__ == '__main__':
    if os.environ.get('FLASK_DEBUG'):
        app.run(debug=True)
    else:
        app.run()