#!/usr/bin/env python

#-----------------------------------------------------------------------
# __init__.py
# Author: Ziv Batscha
#-----------------------------------------------------------------------

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='./templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'very_secret_password'
from paradiselost import routes
