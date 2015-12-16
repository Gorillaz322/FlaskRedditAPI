from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from main import config

app = Flask(__name__, static_url_path='/static')
app.debug = config.DEBUG
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
db = SQLAlchemy(app)

import main.models
import main.views
