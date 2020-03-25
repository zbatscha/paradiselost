#!/usr/bin/env python
from pprint import pprint;
from google.cloud import translate_v2 as translate
import csv
translate_client = translate.Client()
available_languages = translate_client.get_languages()
name_to_iso = {lang['name'].lower() : lang['language'] for lang in available_languages}


def getCountryToLanguage():
    country_to_lang = {}
    with open('./languages.tsv','r') as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')
        for line in tsvin:
            if len(line) == 1:
                country_to_lang[line[0].lower()] = []
                continue
            country, lang = (line[0], [l.lower().strip() for l in line[1].split(',')])
            # remove languages that are not available for translation
            lang = [l.lower() for l in lang if l in name_to_iso.keys()]
            country_to_lang[country.lower()] = lang

    return country_to_lang

def getCountryToIso():
    country_to_lang = getCountryToLanguage()
    country_to_iso = {}
    for country, languages in country_to_lang.items():
        errors = []
        available_isos = []
        for lang in languages:
            available_isos.append({'iso':name_to_iso[lang], 'language':lang})
        country_to_iso[country] = available_isos
    return country_to_iso

def getTotalByCountry():
    data = {}
    name_change = {'congo':'congo'}
    total_deaths = 0
    with open('./time_series_covid19_deaths_global.csv', newline='') as csvfile:
            next(csvfile) # skip header
            datareader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for line in datareader:
                country = line[1].lower().strip('*')
                deaths = int(line[-1])
                total_deaths += deaths
                for dup in name_change.keys():
                    if dup in country:
                        country = name_change[dup]
                if country not in data.keys():
                    data[country] = deaths
                else:
                    data[country] += deaths

    return (data, total_deaths)

def getCountriesByProp(totalByCountry, total):
    countries = [country for country in totalByCountry.keys()]
    prop = [count/total for country, count in totalByCountry.items()]
    return (countries, prop)

if __name__=='__main__':

    country_to_iso = getCountryToIso()
    with open('tools.py', 'w') as out:
        pprint(country_to_iso, stream=out)

    country_to_total, total = getTotalByCountry()
    for country, _ in country_to_total.items():
        if country not in country_to_iso.keys():
            print(f'(ERROR) {country}, Missing from country_to_iso dict')

    (countries, proportion_by_country) = getCountriesByProp(country_to_total, total)
    with open('tools.py', 'a+') as out:
        pprint(countries, stream=out)
        pprint(proportion_by_country, stream=out)
