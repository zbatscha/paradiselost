#!/usr/bin/env python

#-----------------------------------------------------------------------
# language_tools.py
# Author: Ziv Batscha
#-----------------------------------------------------------------------

from paradiselost import db
from paradiselost.models import Record, Country, Language
from datetime import datetime
import numpy as np
import random

#-----------------------------------------------------------------------

"""
Return an array of language tuples (iso, name), each representing a valid
translation code available by the google cloud translate API.
"""
def availableLanguages():
    available_languages = db.session.query(Language.name, Language.iso).all()
    available_languages = [(iso, name.title()) for name, iso in available_languages]
    return available_languages

#-----------------------------------------------------------------------

"""
Return the earliest and latest recorded dates.
"""
def getMinMaxDate():
    dates = db.session.query(Record.date).filter_by(country_id=1).all()
    dates = [date[0].strftime("%Y-%m-%d") for date in dates]
    minDate = min(dates)
    maxDate = max(dates)
    return {'minDate': minDate, 'maxDate': maxDate}

#-----------------------------------------------------------------------

"""
Returns translation mapping by proportion of deaths for each country
on the provided date. Provided a translation count and valid date, returns a
dictionary containing an `iso` key mapped to an array of valid ISO 639-1 codes
available by google cloud translate API and a `language_name` key mapped to an
array of corresponding language names, and a `country_name` key mapped to
an array of countries from which each target language was selected.
"""
def getLanguageByDeaths(count, date):
    country_ids, deaths = list(zip(
        *db.session.query(Record.country_id, Record.deaths).filter_by(
            date=date).filter(Record.deaths>0).all()))
    total_deaths = sum(deaths)
    deaths_props = [record/total_deaths for record in deaths]

    return _getChosenLanguagesByCountry(country_ids, deaths_props, count)

#-----------------------------------------------------------------------

"""
Returns translation mapping by proportion of confirmed cases for each country
on the provided date. Provided a translation count and valid date, returns a
dictionary containing an `iso` key mapped to an array of valid ISO 639-1 codes
available by google cloud translate API and a `language_name` key mapped to an
array of corresponding language names, and a `country_name` key mapped to
an array of countries from which each target language was selected.
"""
def getLanguageByConfirmed(count, date):
    country_ids, confirmed = list(zip(
        *db.session.query(Record.country_id, Record.confirmed).filter_by(
            date=date).filter(Record.confirmed>0).all()))
    total_confirmed = sum(confirmed)
    confirmed_props = [record/total_confirmed for record in confirmed]
    return _getChosenLanguagesByCountry(country_ids, confirmed_props, count)

#-----------------------------------------------------------------------

"""
Returns translation mapping, giving each language the same likelihood for
translation. Provided a translation count and valid date, returns a
dictionary containing an `iso` key mapped to an array of valid ISO 639-1 codes
available by google cloud translate API and a `language_name` key mapped to an
array of corresponding language names.
"""
def getLanguageByEqual(count):
    languages = db.session.query(Language).all()
    equal_props = [1/len(languages)] * len(languages)
    chosen = list(np.random.choice(languages, size=count, p=equal_props))
    chosen_languages = {'iso': [], 'language_name': []}
    for pair in chosen:
        chosen_languages['iso'].append(pair.iso)
        chosen_languages['language_name'].append(pair.name)
    return chosen_languages

#-----------------------------------------------------------------------

"""
Select `count` target languages for translation. Country selection is
weighted by props. Following country selection, a language spoken in that
country is randomly selected as the destination language.
"""
def _getChosenLanguagesByCountry(country_ids, props, count):

    chosen_languages = {'iso': [], 'language_name': [], 'country_name': []}
    for i in range(count):
        while True:
            chosen_country_id = int(np.random.choice(country_ids, p=props))
            country = db.session.query(Country).get(chosen_country_id)
            valid_languages = country.country_languages.all()
            if valid_languages:
                chosen = random.choice(valid_languages)
                chosen_languages['iso'].append(chosen.iso)
                chosen_languages['language_name'].append(chosen.name)
                chosen_languages['country_name'].append(country.name)
                break
    return chosen_languages
