from flask import Flask
from config import Config
import json

#Helper oject to convert to JSON
class Object:
	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class chatMessage:
	def __init__(self,author,message):
		self.author = author
		self.message = message
	def toJSON(self):
		me = Object()
		me.author = self.author
		me.message = self.message
		return me.toJSON()
class chatRoom:
	def __init__(self,author,name):
		self.author = author
		self.name = name
		self.messages = []
	def toJSON(self):
		me = Object()
		me.author = self.author
		me.name = self.name
		me.messages = self.messages
		return me.toJSON()
	def getNewChats(self,chatNumber):
		me = Object()
		me.author = self.author
		me.name = self.name
		me.messages = self.messages[chatNumber:]
		return me.toJSON()
	def getRooms(self):
		me = Object()
		me.name = self.name
		return me.toJSON()



app = Flask(__name__)
app.config.from_object(Config)
rooms = []
users = dict()

from app import routes