from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from main import local, config

app = Flask(__name__)
app.debug = config.DEBUG
app.config['SQLALCHEMY_DATABASE_URI'] = local.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

import main.models
import main.views
