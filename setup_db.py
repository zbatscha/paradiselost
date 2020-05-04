#!/usr/bin/env python

#-----------------------------------------------------------------------
# db_api.py
#-----------------------------------------------------------------------

from paradiselost import app, db
from paradiselost.models import Language, Country, Record
from google.cloud import translate_v2 as translate
from datetime import datetime
import csv
import re
import os

#-----------------------------------------------------------------------

csv_date_start_col = 4
csv_region_col = 1

def _format(country):
    country = country.lower()
    country = re.sub("[^a-z -]+", "", country)
    return country

def get_languages():
    translate_client = translate.Client()
    available_languages = translate_client.get_languages()

    for lang_iso in available_languages:
        language = Language(name=lang_iso['name'].lower(), iso=lang_iso['language'])
        db.session.add(language)
    db.session.commit()

def get_countries():
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
        db.session.add(country)
    db.session.commit()

def get_language_associations():
    with open('./languages.tsv','r') as tsvin:
        tsvin = csv.DictReader(tsvin, delimiter='\t')
        for line in tsvin:
            if len(line) == 1:
                continue
            country = _format(line['country'])
            all_languages = line['languages']
            all_languages = [l.lower().strip() for l in all_languages.split(',')]

            valid_country = Country.query.filter_by(name=country).first()
            if valid_country:
                translate_languages = db.session.query(Language.name).all()
                translate_languages = [l[0] for l in translate_languages]
                errors = []
                for language in all_languages:
                    if language not in translate_languages:
                        errors.append(language)
                    else:
                        lang_row = db.session.query(Language).filter_by(name=language).first()
                        valid_country.country_languages.append(lang_row)
                if errors:
                    print(f'(error), {country}: missing {errors} from {all_languages}')
                    all_languages = [l for l in all_languages if l not in errors]

    db.session.commit()
    
def get_records():
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
            valid_country = db.session.query(Country).filter_by(name=country).first()
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
    db.session.commit()
    print(f'Added {record_count} records to db.')
    global_data.clear()

def populate_db():
    try:
        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()
            get_languages()
            get_countries()
            get_language_associations()
            get_records()
    except Exception as e:
        print(e)

if __name__=='__main__':
    populate_db()
