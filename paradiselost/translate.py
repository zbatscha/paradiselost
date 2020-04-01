#!/usr/bin/env python

#-----------------------------------------------------------------------
# translate.py
# Author: Ziv Batscha
#-----------------------------------------------------------------------

from google.cloud import translate_v2
import paradiselost.language_tools as language_tools
import multiprocessing as mp
import six
import re

#-----------------------------------------------------------------------

# maps language isos that are right justified and read right-to-left
direction_rtl = ['ar', 'iw', 'ku', 'ps', 'fa', 'sd', 'ur', 'ug', 'yi']

#-----------------------------------------------------------------------

"""
Accepts a tuple `text_iso` (text, iso), and makes a request to the google
translate client to translate `text` to the target language represented by the
ISO 639-1 code `iso`. Returns the source_text, translated_text, source_iso, and
translated_iso.
"""
def _translate(text_iso):
    text, translated_iso = text_iso
    translate_client = translate_v2.Client()
    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')
    result = translate_client.translate(
        text, target_language=translated_iso, format_="text")
    source_text = result['input']
    translated_text = result['translatedText']
    source_iso = result['detectedSourceLanguage']
    return source_text, translated_text, source_iso, translated_iso

#-----------------------------------------------------------------------

"""
Prepare source text and translated text for display. Prefixes and appends div
tags with styling.
"""
def _format_html_response(source_text, translated_text, source_iso, translated_iso):

    f_source_text = []
    f_translated_text = []

    # if language is right-justified, append text-align styling to div.
    # maintain whitespace for all lines
    for i, line in enumerate(source_text):
        if source_iso[i] in direction_rtl:
            f_source_text.append('<div style="white-space: pre; \
            text-align:right;direction:rtl">' + line + '</div>')
        else:
            f_source_text.append('<div style="white-space: pre">' + line + '</div>')

    for i, line in enumerate(translated_text):
        if translated_iso[i] in direction_rtl:
            f_translated_text.append('<div style="white-space: pre; \
            text-align:right;direction:rtl">' + line + '</div>')
        else:
            f_translated_text.append('<div style="white-space: pre">' + line + '</div>')

    return f_source_text, f_translated_text

#-----------------------------------------------------------------------

"""
Returns a line by line translation for text given the provided data selection
method and valid date for sourcing country records. Methods include 'humanToll'
and 'equal':
- 'humanToll' uses the death rate for weighting language translation.
- 'equal' provided equal weighting for all languages.
Returns the source_text and translated_text as strings.
"""
def getTranslation(text, method, date):
    text = text.strip()
    text = text.split('\n')
    prepared_text = [line for line in text]
    translation_count = len(prepared_text)

    if method == 'humanToll':
        languages = language_tools.getLanguageByDeaths(translation_count, date)
    # elif method == 'confirmed':
    #     languages = language_tools.getLanguageByConfirmed(translation_count, date)
    else:
        languages = language_tools.getLanguageByEqual(translation_count)

    # map lines to language iso codes, send lines for multiprocessing translation
    translation_pairs = list(zip(prepared_text, languages['iso']))
    p = mp.Pool(mp.cpu_count())
    output = p.map(_translate, translation_pairs)

    source_text, translated_text, source_iso, translated_iso = list(zip(*output))
    source_text, translated_text = _format_html_response(source_text,
                                    translated_text, source_iso, translated_iso)

    source_text = "".join(source_text)
    translated_text = "".join(translated_text)

    return (source_text, translated_text)
