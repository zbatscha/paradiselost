#!/usr/bin/env python

#-----------------------------------------------------------------------
# routes.py
# Author: Ziv Batscha
#-----------------------------------------------------------------------

from paradiselost import app
from flask import render_template, url_for, flash, redirect, request
from paradiselost.forms import PoemForm
import paradiselost.translate as translate

#-----------------------------------------------------------------------

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    form = PoemForm()
    poem = ""
    translated_poem = ""
    if form.validate_on_submit():
        try:
            if form.url.errors or not form.url.data:
                (poem, translated_poem) = translate.getTextTranslation(form.body.data)
            else:
                (poem, translated_poem) = translate.getURLTranslation(form.url.data)
        except Exception as e:
            flash('Error translating provided poem.', 'danger')
            print('(Error) ', e.args[0])
    return render_template('home.html', poem=poem, translated_poem=translated_poem, form=form)

#-----------------------------------------------------------------------

@app.route("/about")
def about():
    return render_template('about.html', title='About')
