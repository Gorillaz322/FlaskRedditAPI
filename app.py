from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = \
    "postgresql://postgres:123@localhost/flask_reddit_api"
db = SQLAlchemy(app)

from main import models, views