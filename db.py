from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class School(db.Model):
    name = db.Column(db.String(100), primary_key=True, unique=True, nullable=False)
    abbrev = db.Column(db.String(50), unique=False, nullable=False)
    council = db.Column(db.Boolean, unique=False, nullable=False)