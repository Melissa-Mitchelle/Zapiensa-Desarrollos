from datetime import timedelta
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)


class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'ZAP/IENSA'
    DEBUG = True
    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///zapiensa_project_v2.db'  # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = 'Eventos Ayuntamiento'  # Shown in and email templates and page footers
    SECURITY_USER_IDENTITY_ATTRIBUTES = 'username'
    SECURITY_PASSWORD_SALT = 'ZAPIENSAD'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
    WTF_CSRF_ENABLED = False
    SECURITY_UNAUTHORIZED_VIEW = None

    # Flask-Security Settings
    """SECURITY_MSG_EMAIL_NOT_PROVIDED = 'Ingrese un nombre de usuario'
    SECURITY_MSG_INVALID_EMAIL_ADDRESS = 'Usuario invalido'
    SECURITY_MSG_INVALID_PASSWORD = 'Contrasena invalida'
    SECURITY_MSG_PASSWORD_NOT_PROVIDED = 'Ingrese una contrasena'
    SECURITY_MSG_USER_DOES_NOT_EXIST = 'No existe este usuario'"""


app.config.from_object(__name__ + '.ConfigClass')
db = SQLAlchemy(app)
