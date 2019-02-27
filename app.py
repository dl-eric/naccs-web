from flask import Flask, render_template, session, request
from auth import auth_page
from news import news_page
import os
from matches import Matches

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.register_blueprint(auth_page)
app.register_blueprint(news_page)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', username=session.get('username')), 404

@app.route('/')
def index():
    headers = {
        "User-Agent": request.headers.get('User-Agent'),
        "Referer": request.url
    }

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
