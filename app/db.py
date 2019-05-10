from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class CountryType(str, enum.Enum):
    USA = "USA"
    CA  = "CA"
    MX  = "MX"

class School(db.Model):
    name            = db.Column(db.String(100), primary_key=True, unique=True, nullable=False)
    abbrev          = db.Column(db.String(50), unique=False, nullable=False)
    council         = db.Column(db.Boolean, unique=False, nullable=False)
    city            = db.Column(db.String(100), unique=False, nullable=False)
    state           = db.Column(db.String(100), unique=False, nullable=False)
    country         = db.Column(db.Enum(CountryType), nullable=False)
    logo_path       = db.Column(db.String, unique=False, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
           'name'       : self.name,
           'council'    : self.council,
           'city'       : self.city,
           'state'      : self.state,
           'country'    : self.country,
           'logo_path'  : self.logo_path
        }

class Teams(db.Model):
    team_id         = db.Column(db.Integer, primary_key=True)
    school          = db.Column(db.String(255), unique=True, nullable=False)
    name            = db.Column(db.String(255), unique=False, nullable=False)
    team_type       = db.Column(db.String(255), unique=False, nullable=False)
    leader          = db.Column(db.String(255), unique=False, nullable=False)
    password        = db.Column(db.String(255), unique=False, nullable=False)

    def __init__ (self, school, name, team_type, leader, password):
        self.school = school
        self.name = name
        self.team_type = team_type
        self.leader = leader
        self.password = password
    

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

class Players(db.Model):
    player_id       = db.Column(db.Integer, primary_key=True)
    name              = db.Column(db.String(255), primary_key=False, unique=False, nullable=False)
    school           = db.Column(db.String(255), primary_key=False, unique=False, nullable=True)
    team_id         = db.Column(db.Integer, primary_key=False, unique=False, nullable=False)
    paid            = db.Column(db.String(5), primary_key=False, unique=False, nullable=False)

    def __init__ (self, name, school, team_id, paid):
        self.name       = name
        self.school     = school
        self.team_id    = team_id
        self.paid       = paid

class Payments(db.Model):
    name       = db.Column(db.String(255), primary_key=True)
    paymentid              = db.Column(db.String(255), primary_key=False, unique=False, nullable=False)
    payerid           = db.Column(db.String(255), primary_key=False, unique=False, nullable=True)
    date           = db.Column(db.String(255), primary_key=False, unique=False, nullable=True)


    def __init__ (self, name, paymentid, payerid, date):
        self.name       = name
        self.paymentid     = paymentid
        self.payerid    = payerid
        self.date       = date
        
        
