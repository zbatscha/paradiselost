#!/usr/bin/env python

#-----------------------------------------------------------------------
# routes.py
# Author: Ziv Batscha
#-----------------------------------------------------------------------

from flask import render_template, url_for, flash, redirect, request, Markup, jsonify
from paradiselost.forms import PoemForm
import paradiselost.translate as translate
from paradiselost.language_tools import getMinMaxDate
from paradiselost import app
from sys import stderr

#-----------------------------------------------------------------------

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    poem = ""
    translated_poem = ""
    dateRange = None
    form = PoemForm()
    try:
        dateRange = getMinMaxDate()
        if form.validate_on_submit():
            (poem, translated_poem) = translate.getTranslation(form.body.data,
                                                               form.choice.data,
                                                               form.date.data)
    except Exception as e:
        flash('Error translating provided poem.', 'danger')
        print(e, file=stderr)
    return render_template('home.html', poem=Markup(poem),
                            translated_poem=Markup(translated_poem),
                            dateRange=dateRange, form=form)

#-----------------------------------------------------------------------

@app.route("/about")
def about():
    return render_template('about.html', title='About')
