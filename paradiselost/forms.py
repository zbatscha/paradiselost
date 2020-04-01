#!/usr/bin/env python

#-----------------------------------------------------------------------
# forms.py
# Author: Ziv Batscha
#-----------------------------------------------------------------------

from flask import flash
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, DateField, RadioField, SelectField
from wtforms.validators import DataRequired, ValidationError, Optional
from paradiselost.language_tools import getMinMaxDate
from datetime import datetime

#-----------------------------------------------------------------------

"""
TextArea field on home page.
"""
class PoemForm(FlaskForm):
    body = TextAreaField('Paste your song, poem, or memory',  validators=[DataRequired()])
    choice = RadioField('Choose language by...  ', validators=[DataRequired()],
                        choices=[('humanToll', 'Human Toll'),
                                 ('equal', 'Equal Likelihood')], default='deaths')
    date = DateField('Select data source date', default=datetime.strptime(
                                getMinMaxDate()['maxDate'], '%Y-%m-%d').date(),
                                validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_body(self, body):
        text = body.data.strip()
        if len(text) >= 3000:
            raise ValidationError('Maximum length of 3000 characters allowed.')
        if len(text) == 0:
            raise ValidationError('Please provide your selected text.')
