#!/usr/bin/env python

#-----------------------------------------------------------------------
# translate.py
# Author: Ziv Batscha
#-----------------------------------------------------------------------

from breath.language_tools import country_to_languages, countries, proportion
from google.cloud import translate_v2
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import numpy as np
import random
import csv
import six
import re

#-----------------------------------------------------------------------

"""
Choose a random country by the proportion.
"""
def getCountryByProp():
    chosen = np.random.choice(countries, p=proportion)
    return chosen

#-----------------------------------------------------------------------

"""
Return random ISO from provided country.
"""
def getDestinationISO(country):
    languages = country_to_languages[country]
    if not languages:
        return None
    lang_iso = random.choice(languages)
    return lang_iso

#-----------------------------------------------------------------------

"""
Returns a list with line_count dictionaries.
Each dictionary contains the keys: 'iso', 'language', 'country'.
"""
def getISOS(line_count):
    all_isos = [None] * line_count
    for i in range(line_count):
        while True:
            country = getCountryByProp()
            lang_iso = getDestinationISO(country)
            if lang_iso:
                lang_iso['country'] = country
                all_isos[i] = lang_iso
                break
    return all_isos

#-----------------------------------------------------------------------

"""
Translate text to destination given by iso. Calls Google Cloud Translate API.
"""
def _translate(text, iso):
    translate_client = translate_v2.Client()
    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')
    result = translate_client.translate(
        text, target_language=iso, format_="text")
    translated_text = result['translatedText']
    return translated_text

#-----------------------------------------------------------------------

def getTranslation(prepared_poem):

    isos_lang_country = getISOS(len(prepared_poem))
    original_poem = ''
    translated_poem = ''
    for i, line in enumerate(prepared_poem):
        spaces = re.findall('^\s*', line)
        text_for_translation = line.strip()
        iso = isos_lang_country[i]['iso']
        translated_text = _translate(text_for_translation, iso)
        original_poem += spaces[0] + text_for_translation + '\n'
        translated_poem += spaces[0] + translated_text + '\n'
    return (original_poem, translated_poem)

#-----------------------------------------------------------------------

def getTextTranslation(poem):
    prepared_poem = poem.split('\n')
    prepared_poem = [line.strip() for line in prepared_poem if line]
    return getTranslation(prepared_poem)

#-----------------------------------------------------------------------

def getURLTranslation(site):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(site,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page, 'html.parser')
    mydivs = soup.findAll("div", {"class": "o-poem"})
    soup = mydivs[0]
    divs = soup.findAll("div")
    poem = []
    for line in divs:
        poem.append(line.text) # reverted to html, use line.text otherwise
    # poem = "\n".join(poem).strip()
    # prepared_poem = re.split('(?<=[;.!?])', poem)
    return getTranslation(poem)

if __name__=='__main__':
    # print(getCountryByProp())
    # print(getISOS(20))
    # print(_translate('how\'s your day \'\'.', 'he'))
    getURLTranslation('https://www.poetryfoundation.org/poetrymagazine/poems/56261/among-women')
