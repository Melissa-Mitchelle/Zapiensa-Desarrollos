from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)


class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'
    DEBUG = True
    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = 'Eventos Ayuntamiento'      # Shown in and email templates and page footers
    SECURITY_USER_IDENTITY_ATTRIBUTES = 'username'
    SECURITY_PASSWORD_SALT = 'ZAPIENSAD'

app.config.from_object(__name__+'.ConfigClass')
db = SQLAlchemy(app)
