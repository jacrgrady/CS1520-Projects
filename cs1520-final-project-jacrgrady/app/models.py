from datetime import datetime,date
from app import db
from hashlib import md5
from flask import url_for

class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True, nullable=False)
	password_hash = db.Column(db.String(128), nullable=False)
	categories = db.relationship('Category', backref='user', lazy=True)


class Category(db.Model):
	__tablename__ = 'category'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, nullable=False)
	limit = db.Column(db.Integer, index=True, nullable=False)
	parent_id =  db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
	purchases = db.relationship('Purchase', backref='category', lazy=True)

	def to_dict(self):
		data = {
			'id': self.id,
			'name': self.name,
			'limit': self.limit,
			'parent_id': self.parent_id
		}
		return data
	def from_dict(self, data):
		for field in ['name', 'limit', 'parent_id']:
			if field in data:
				setattr(self, field, data[field])

class Purchase(db.Model):
	__tablename__ = 'purchase'
	id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String(120), index=True)
	amount = db.Column(db.Integer, index=True, nullable=False)
	date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	category_id = db.Column(db.Integer, db.ForeignKey('category.id'),nullable=False)

	def to_dict(self):
		data = {
			'id': self.id,
			'description': self.description,
			'amount': self.amount,
			'date': self.date.__str__(),
			'category_id': self.category_id
		}
		return data	

	def from_dict(self, data):
		for field in ['description', 'amount','category_id']:
			if field in data:
				setattr(self, field, data[field])
