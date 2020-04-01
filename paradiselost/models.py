#!/usr/bin/env python

#-----------------------------------------------------------------------
# models.py
#-----------------------------------------------------------------------

from paradiselost import db

subs = db.Table('subs',
    db.Column('country_id', db.Integer, db.ForeignKey('country.country_id')),
    db.Column('language_id', db.Integer, db.ForeignKey('language.language_id')))

class Language(db.Model):
    __tablename__ = 'language'
    language_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    iso = db.Column(db.String(10), nullable=False)
    subscriptions = db.relationship('Country', secondary='subs', backref=db.backref('country_languages', lazy='dynamic'))

    def __repr__(self):
        return f"Language('{self.name}', '{self.iso}')"

class Country(db.Model):
    __tablename__ = 'country'
    country_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    country_records = db.relationship("Record", back_populates="country")

    def __repr__(self):
        return f"Country('{self.name}')"

class Record(db.Model):
    __tablename__ = 'records'
    __table_args__ = (db.UniqueConstraint('country_id', 'date'),)

    record_id = db.Column(db.Integer, primary_key=True)
    confirmed = db.Column(db.Integer, nullable=True)
    confirmed_prop = db.Column(db.Float, nullable=True)
    deaths = db.Column(db.Integer, nullable=True)
    deaths_prop = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, nullable=False)

    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'))
    country = db.relationship("Country", back_populates="country_records")

    def __repr__(self):
        return f"Record('{self.country}', ('{self.confirmed}', '{self.confirmed_prop}') ('{self.deaths}', '{self.deaths_prop}') '{self.date}')"
