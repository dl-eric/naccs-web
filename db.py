from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class School(db.Model):
    name            = db.Column(db.String(100), primary_key=True, unique=True, nullable=False)
    abbrev          = db.Column(db.String(50), unique=False, nullable=False)
    council         = db.Column(db.Boolean, unique=False, nullable=False)

class Article(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    title           = db.Column(db.String(200), nullable=False)
    author          = db.Column(db.String(50), nullable=False)
    author_username = db.Column(db.String(50), nullable=False)
    date            = db.Column(db.Date, nullable=False)
    content         = db.Column(db.String, nullable=False)
    summary         = db.Column(db.String, nullable=False)
    image_path      = db.Column(db.String(100), nullable=False)

    def __init__ (self, title, author, author_username, content, summary, image_path='https://s3.us-east-2.amazonaws.com/naccs-s3/headerbanner_wide.png'):
        self.title = title 
        self.author = author 
        self.author_username = author_username
        self.date = datetime.now()
        self.content = content 
        self.summary = summary
        self.image_path = image_path
