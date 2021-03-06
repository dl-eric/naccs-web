from flask import Flask, render_template, session, request
from auth import auth_page
from news import news_page
from schools import schools_page
import os
from matches import Matches
from db import db, School

db_user       = os.environ.get('DB_USER')
db_password   = os.environ.get('DB_PASSWORD')
db_db         = os.environ.get('DB_DB')
db_host       = os.environ.get('DB_HOST')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{0}:{1}@{2}/{3}'.format(db_user, db_password, db_host, db_db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(auth_page)
app.register_blueprint(news_page)
app.register_blueprint(schools_page)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

db.init_app(app)

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
    
    return render_template("index.html", matches=matches)

if __name__ == '__main__':
    if os.environ.get('FLASK_DEBUG'):
        app.run(debug=True)
    else:
        app.run()
