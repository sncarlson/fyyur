# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
import datetime

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app import db



class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

    def get_venue(self):
        venue = {
            "id": self.id,
            "name": self.name,
            "num_upcoming_shows": self.get_upcoming_shows_count(),
        }
        return venue

    def get_upcoming_shows_count(self):
        now = datetime.datetime.now()
        upcoming_shows_query = db.session.query(Show) \
            .filter(Show.venue_id == self.id) \
            .filter(Show.start_time > now) \
            .all()
        return len(upcoming_shows_query)

    def get_past_shows_count(self):
        now = datetime.datetime.now()
        upcoming_shows_query = db.session.query(Show) \
            .filter(Show.venue_id == self.id) \
            .filter(Show.start_time < now) \
            .all()
        return len(upcoming_shows_query)

    @property
    def search(self):
        return {
            'id': self.id,
            'name': self.name,
            "num_upcoming_shows": self.get_upcoming_shows_count()
        }


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy=True, passive_deletes=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

    def get_upcoming_shows_count(self):
        now = datetime.datetime.now()
        upcoming_shows_query = db.session.query(Show) \
            .filter(Show.artist_id == self.id) \
            .filter(Show.start_time > now) \
            .all()
        return len(upcoming_shows_query)

    def get_past_shows_count(self):
        now = datetime.datetime.now()
        upcoming_shows_query = db.session.query(Show) \
            .filter(Show.artist_id == self.id) \
            .filter(Show.start_time < now) \
            .all()
        return len(upcoming_shows_query)

    @property
    def search(self):
        return {
            'id': self.id,
            'name': self.name,
            "num_upcoming_shows": self.get_upcoming_shows_count()
        }


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime())

    def __repr__(self):
        return f'<Venue {self.id}>'
