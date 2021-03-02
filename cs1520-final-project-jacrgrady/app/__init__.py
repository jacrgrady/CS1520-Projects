from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource

#this contains init data for the app
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('category',location='json')
parser.add_argument('purchase',location='json')
from app import routes, models