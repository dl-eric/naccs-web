from flask_sqlalchemy import SQLAlchemy

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
    summary         = db.Column(db.String(200), nullable=False)
    image_path      = db.Column(db.String(100), nullable=False)
