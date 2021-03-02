import os
from hashlib import md5
from datetime import datetime,date
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack,jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User,Category,Purchase
from app import app,db,api,parser
from functools import wraps
from flask_restful import reqparse, abort, Api, Resource

import datetime

#start up
@app.cli.command('initdb')
def initdb_command():
	db.create_all()
	print('Initialized the database.')

@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter_by(id=session['user_id']).first()

def require_login(func):
	#function to check if the user is logged in
	@wraps(func)
	def function(*args, **kws):
		if not g.user:
			return redirect(url_for('index'))
		return func(*args, **kws)
	return function

def convert_datetime(date_in):
	date_processing = date_in.replace('T', '-').replace(':', '-').split('-')
	date_processing = [int(v) for v in date_processing]
	return datetime.date(*date_processing)

def get_user_id(username):
	rv = User.query.filter_by(username=username).first()
	return rv.id if rv else None

def reverse_date(date):
	return datetime.date(date.year, date.month, date.day)

def first_date(date):
	return datetime.date(date.year, date.month, 1)

def last_date(date):
	if date.month == 12:
		return datetime.date(date.year, date.month, 31)
	return reverse_date(date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1))

def getMonth():
	return date.today().strftime("%B")

def make_error(err):
	return {"ERROR":err},404


def get_cat_by_name(name):
	for cat in Category.query.all():
		if cat.name == name:
			return cat

#If the user logs in then sends the user back
#else sends the first user back so that
#You have to log into the client to use the API properly
def get_user():
	if g.user:
		return g.user
	else:
		return User.query.get(1)

#API functions
class RESTCategoryList(Resource):
	def get(self):
		data = []
		for cat in Category.query.all():
			if cat.parent_id == get_user().id:
				data.append(cat.to_dict())
		return {"categories":data},200

	def post(self):
		data = request.get_json(force=True)['category']
		if not get_user():
			return make_error("Incorrect login info")
		if 'name' not in data or 'limit' not in data:
			return {"ERROR":"BAD REQUEST"},404
		category = Category()
		category.from_dict(data)
		u = get_user()
		u.categories.append(category)
		db.session.commit()
		return category.to_dict(),201

class RESTCategory(Resource):
	def delete(self, id):
		cat = Category.query.get(id)
		if cat == None:
			return make_error("ID does not exist")
		no_cat = get_cat_by_name("NONE")
		for p in cat.purchases:
			p.category_id = no_cat.id
		db.session.commit()
		db.session.delete(cat)
		db.session.commit()
		return cat.to_dict(),204

class RESTPurchase(Resource):
	def get(self):
		if not g.user:
			return {"purchases":"log in"},200
		data = []
		for purchase in Purchase.query.all():
			if Category.query.get(purchase.category_id).parent_id == get_user().id:
				data.append(purchase.to_dict())
		return {"purchases":data},200

	def post(self):
		data = request.get_json(force=True)['purchase']
		if 'description' not in data or 'amount' not in data or 'date' not in data or 'category_id' not in data:
			return make_error("Please fill out all fields")
		purchase = Purchase()
		purchase.from_dict(data)

		date_arr = data['date'].split('-')
		purchase.date = datetime.date(int(date_arr[0]),int(date_arr[1]),int(date_arr[2]))


		cat = Category.query.get_or_404(purchase.category_id)
		cat.purchases.append(purchase)
		db.session.commit()
		
		return purchase.to_dict(),201

api.add_resource(RESTCategoryList, '/cats')
api.add_resource(RESTCategory, '/cats/<id>')
api.add_resource(RESTPurchase, '/purchases')


@app.route("/")
@app.route('/index')
def index():
	user = g.user
	categories = None
	if g.user:
		categories=user.categories
	return render_template('index.html', user=user,categories=categories,month = getMonth())

@app.route('/addPurchase', methods=['GET', 'POST'])
@require_login
def addPurchase():
	error = None
	categories = g.user.categories[1:]#skip NONE category
	current_date = datetime.datetime.now()
	return render_template('addPurchase.html', error=error,categories=categories,first_day=first_date(current_date),last_day=last_date(current_date))

@app.route("/newCategory", methods=['GET', 'POST'])
@require_login
def newCategory():
	return render_template('newCategory.html')

@app.route("/deleteCategory", methods=['GET', 'POST'])
@require_login
def deleteCategory():
	error = None
	categories = g.user.categories[1:]#skip NONE category
	return render_template('deleteCategory.html', error=error,categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		if not request.form['username']:
			error = 'You have to enter a username'
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'The two passwords do not match'
		elif get_user_id(request.form['username']) is not None:
			error = 'This username is already taken'
		else:
			u = User(username=request.form['username'], password_hash=generate_password_hash(request.form['password']))
			u.categories.append(Category(name="NONE",limit=0,parent_id=u.id))
			db.session.add(u)
			db.session.commit()
			flash('You were successfully registered and can login now')
			return redirect(url_for('login'))
	return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if g.user:
		return redirect(url_for('index'))
	error = None
	if request.method == 'POST':

		user = User.query.filter_by(username=request.form['username']).first()
		if user is None or not check_password_hash(user.password_hash, request.form['password']):
			error = 'Invalid username or password'
		else:
			session['user_id'] = user.id
			return redirect(url_for('index'))
	return render_template('login.html', error=error)


@app.route('/logout')
def logout():
	session.pop('user_id', None)
	return redirect(url_for('index'))