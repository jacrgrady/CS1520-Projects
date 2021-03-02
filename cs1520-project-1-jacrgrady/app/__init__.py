from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

#this contains init data for the app
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from app import routes, models