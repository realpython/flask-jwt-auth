# project/server/__init__.py

import os
import sys

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

if sys.version_info >= (3, 4):
    py_version = 3
elif sys.version_info >= (2, 7):
    py_version = 2

app = Flask(__name__)
CORS(app)

app_settings = os.getenv(
    'APP_SETTINGS',
    'project.server.config.DevelopmentConfig'
)
app.config.from_object(app_settings)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

from project.server.auth.views import auth_blueprint

app.register_blueprint(auth_blueprint)
