#!/usr/bin/env python

#-----------------------------------------------------------------------
# forms.py
# Author: Ziv Batscha
#-----------------------------------------------------------------------

from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Optional
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

#-----------------------------------------------------------------------

class PoemForm(FlaskForm):
    url = StringField('Poem URL', validators=[Optional()])
    body = TextAreaField('OR paste your poem',  validators=[Optional()])
    submit = SubmitField('Submit')

    def validate(self):
        if not super(PoemForm, self).validate():
            return False
        url = self.url.data.strip()
        text = self.body.data.strip()
        if not url and not text:
            flash('At least one submission option must be set', 'danger')
            return False
        elif url:
            if self.validateURL(url):
                flash('Using provided URL for translation!', 'success')
                return True
            else:
                msg = 'Please provide a valid poetryfoundation.org url to your selected poem.'
                self.url.errors.append(msg)
        elif not text:
            return False
        else:
            if len(text) >= 3000:
                msg = 'Maximum length of 3000 characters allowed.'
                self.body.errors.append(msg)
                return False
        flash('Using provided text for translation!', 'success')
        return True

    def validateURL(self, url):
        if 'poetryfoundation.org/poems' not in url:
            return False
        try:
            hdr = {'User-Agent': 'Mozilla/5.0'}
            req = Request(url ,headers=hdr)
            page = urlopen(req)
            soup = BeautifulSoup(page, 'html.parser')
            mydivs = soup.findAll("div", {"class": "o-poem"})
            soup = mydivs[0]
        except:
            # raise ValidationError('Please provide a valid poetryfoundation.org url to your selected poem.')
            return False
        return True
