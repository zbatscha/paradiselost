#!/usr/bin/env python

#-----------------------------------------------------------------------
# db_setup.py
#-----------------------------------------------------------------------

from datetime import datetime
from sqlalchemy import create_engine, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, String, Integer, Text, Date, ForeignKey, Boolean, Table, Float
import os
#-----------------------------------------------------------------------

DB_URL = os.getenv('DATABASE_URL')
db = create_engine(DB_URL)
base = declarative_base()

subs = Table('subs', base.metadata,
    Column('country_id', Integer, ForeignKey('country.country_id')),
    Column('language_id', Integer, ForeignKey('language.language_id')))

class Language(base):
    __tablename__ = 'language'
    language_id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    iso = Column(String(10), nullable=False)
    subscriptions = relationship('Country', secondary='subs', backref=backref('country_languages', lazy='dynamic'))

    def __repr__(self):
        return f"Language('{self.name}', '{self.iso}')"

class Country(base):
    __tablename__ = 'country'
    country_id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    country_records = relationship("Record", back_populates="country")

    def __repr__(self):
        return f"Country('{self.name}')"

class Record(base):
    __tablename__ = 'records'
    __table_args__ = (UniqueConstraint('country_id', 'date'),)

    record_id = Column(Integer, primary_key=True)
    confirmed = Column(Integer, nullable=True)
    confirmed_prop = Column(Float, nullable=True)
    deaths = Column(Integer, nullable=True)
    deaths_prop = Column(Float, nullable=True)
    date = Column(Date, nullable=False)

    country_id = Column(Integer, ForeignKey('country.country_id'))
    country = relationship("Country", back_populates="country_records")

    def __repr__(self):
        return f"Record('{self.country}', ('{self.confirmed}', '{self.confirmed_prop}') ('{self.deaths}', '{self.deaths_prop}') '{self.date}')"

base.metadata.drop_all(db)
base.metadata.create_all(db)
