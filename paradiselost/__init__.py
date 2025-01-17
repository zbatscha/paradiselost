#!/usr/bin/env python

#-----------------------------------------------------------------------
# __init__.py
# Author: Ziv Batscha
#-----------------------------------------------------------------------

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='./templates', static_folder="./static")

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from paradiselost import routes
