#!/usr/bin/env python

#-----------------------------------------------------------------------
# db_api.py
#-----------------------------------------------------------------------

from pprint import pprint
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from google.cloud import translate_v2 as translate
from db_setup import Language, Country, Record, base
import numpy as np
import random
import csv
import re
import time
import os

#-----------------------------------------------------------------------

DB_URL = os.getenv('DATABASE_URL')
csv_date_start_col = 4
csv_region_col = 1

def create_session():
    db = create_engine(DB_URL)
    base.metadata.bind = db
    DBSession = sessionmaker(bind=db,autoflush=False)
    session = DBSession()
    return session

def _format(country):
    country = country.lower()
    country = re.sub("[^a-z -]+", "", country)
    return country

def get_languages(session):
    translate_client = translate.Client()
    available_languages = translate_client.get_languages()
    for lang_iso in available_languages:
        language = Language(name=lang_iso['name'].lower(), iso=lang_iso['language'])
        session.add(language)

def get_countries(session):
    translation_countries = set()
    with open('./languages.tsv','r') as tsvin:
        datareader = csv.DictReader(tsvin, delimiter='\t')
        for line in datareader:
            country = _format(line['country'])
            translation_countries.add(country)

    covid_countries = set()
    with open('./time_series_covid19_deaths_global.csv', newline='') as csvfile:
        datareader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        fieldnames = datareader.fieldnames
        region_header = fieldnames[csv_region_col]
        for line in datareader:
            country = _format(line[region_header])
            covid_countries.add(country)

    missing = covid_countries-translation_countries
    if missing:
        print('(error) countries only in covid tracker: ', missing)
    for country in sorted(list(covid_countries-missing)):
        country = Country(name=country)
        session.add(country)

def get_language_associations(session):
    with open('./languages.tsv','r') as tsvin:
        tsvin = csv.DictReader(tsvin, delimiter='\t')
        for line in tsvin:
            if len(line) == 1:
                continue
            country = _format(line['country'])
            all_languages = line['languages']
            all_languages = [l.lower().strip() for l in all_languages.split(',')]

            valid_country = session.query(Country).filter_by(name=country).first()
            if valid_country:
                translate_languages = session.query(Language.name).all()
                translate_languages = [l[0] for l in translate_languages]
                errors = []
                for language in all_languages:
                    if language not in translate_languages:
                        errors.append(language)
                    else:
                        lang_row = session.query(Language).filter_by(name=language).first()
                        valid_country.country_languages.append(lang_row)
                if errors:
                    print(f'(error), {country}: missing {errors} from {all_languages}')
                    all_languages = [l for l in all_languages if l not in errors]

def get_records(session):
    global_data = {}

    with open('./time_series_covid19_deaths_global.csv', newline='') as csvfile:
        datareader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        fieldnames = datareader.fieldnames
        dates = fieldnames[csv_date_start_col:]
        region_header = fieldnames[csv_region_col]
        global_data = {}
        total_global = {day: {'deaths': 0, 'confirmed': 0} for day in dates}

        for line in datareader:
            country = _format(line[region_header])
            if country not in global_data:
                global_data[country] = {day: {'deaths': 0, 'confirmed': 0} for day in dates}
            for day in dates:
                global_data[country][day]['deaths'] += int(line[day])
                total_global[day]['deaths'] += int(line[day])

    with open('./time_series_covid19_confirmed_global.csv', newline='') as csvfile:
        datareader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        fieldnames = datareader.fieldnames
        dates = fieldnames[csv_date_start_col:]
        region_header = fieldnames[csv_region_col]
        for line in datareader:
            country = _format(line[region_header])
            if country not in global_data:
                print(f'Error {country}')
            else:
                for day in dates:
                    global_data[country][day]['confirmed'] += int(line[day])
                    total_global[day]['confirmed'] += int(line[day])

    record_count = 0
    for country, days in global_data.items():
        for day, data in days.items():
            day_field = datetime.strptime(day, '%m/%d/%y').date()
            recorded = datetime.strptime(day, '%m/%d/%y').date()
            total_confirmed = total_global[day]['confirmed']
            total_deaths = total_global[day]['deaths']
            confirmed_prop = data['confirmed']/total_confirmed
            deaths_prop = data['deaths']/total_deaths
            valid_country = session.query(Country).filter_by(name=country).first()
            if valid_country:
                record = Record(confirmed=data['confirmed'],
                                 deaths=data['deaths'],
                                 confirmed_prop=confirmed_prop,
                                 deaths_prop=deaths_prop,
                                 date=recorded)
                valid_country.country_records.append(record)
                record_count += 1
            else:
                print(f'(error) {country} not in db.')
    print(f'Added {record_count} records to db.')
    global_data.clear()

def populate_db():
    session = create_session()
    try:
        get_languages(session)
        get_countries(session)
        session.commit()
        get_language_associations(session)
        session.commit()
        get_records(session)
        session.commit()
    except Exception as e:
        print('rolling back')
        session.rollback()
        print(e)
    finally:
        session.close()

if __name__=='__main__':
    populate_db()
