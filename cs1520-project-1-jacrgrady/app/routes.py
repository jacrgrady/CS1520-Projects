from app import app

import time
import os
from hashlib import md5
from datetime import datetime,date
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User,Event
from app import db
from functools import wraps


#helper methods
def convert_datetime(date_in):
	date_processing = date_in.replace('T', '-').replace(':', '-').split('-')
	date_processing = [int(v) for v in date_processing]
	return datetime(*date_processing)
	
def get_user_id(username):
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None


def require_login(func):
	#function to check if the user is logged in
	@wraps(func)
	def function(*args, **kws):
		if not g.user:
			return redirect(url_for('index'))
		return func(*args, **kws)
	return function

#start up
@app.cli.command('initdb')
def initdb_command():
	db.create_all()
	print('Initialized the database.')

@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter_by(user_id=session['user_id']).first()


#routes
@app.route('/')
@app.route('/index')
def index():
	user = g.user
	events = Event.query.order_by(Event.start_time.asc())
	return render_template('index.html', title='Home', user=user, events=events)

@app.route('/event/<id>')
def event(id):
	event = Event.query.get(id)
	users = event.users
	hosted_user = User.query.get(event.hosted_user_id)
	return render_template('event.html', title='Event', users=users, event=event, hosted_user=hosted_user)

@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    events = user.events
    return render_template('user.html', user=user, events=events)



@app.route('/Create_Event', methods=['GET', 'POST'])
@require_login
def create_event():
	error = None
	if request.method == 'POST':
		if not request.form.get('title'):
			error = 'You have to enter a title'
		elif not request.form.get('description'):
			error = 'You have to enter a description'
		elif not request.form.get('start-time'):
			error = 'You have to enter a start'
		elif not request.form.get('end-time'):
			error = 'You have to enter a end'
		elif request.form.get('start-time') >= request.form.get('end-time'):
			error = "You have to enter an end date after the start"
		else:
			e = Event(title=request.form.get('title'),body=request.form.get('description'),start_time=convert_datetime(request.form.get('start-time')),end_time=convert_datetime(request.form.get('end-time')),hosted_user_id=g.user.user_id)
			e.users.append(g.user)
			db.session.add(e)
			db.session.commit()
			return redirect(url_for('index'))
	return render_template('create_event.html',error=error)

@app.route("/delete_event", methods=['GET', 'POST'])
@require_login
def delete_event():
	event_id = request.args.get('event_id')
	if g.user.user_id != Event.query.get(event_id).hosted_user_id:
		return redirect(url_for('index'))
	if request.method == 'POST':
		db.session.delete(Event.query.get(event_id))
		db.session.commit()
		return redirect(url_for('index'))
	return render_template("delete.html")

@app.route("/Add_Event", methods=['GET', 'POST'])
@require_login
def add_event():
	event_id = request.args.get('event_id')
	if g.user in Event.query.get(event_id).users or g.user.user_id == Event.query.get(event_id).hosted_user_id:
		return redirect(url_for('index'))
	if request.method == 'POST':
		g.user.events.append(Event.query.get(event_id))
		db.session.commit()
		return redirect(url_for('index'))
	return render_template("add_event.html")

@app.route("/Remove_Event", methods=['GET', 'POST'])
@require_login
def remove_event():
	event_id = request.args.get('event_id')
	if g.user not in Event.query.get(event_id).users or g.user.user_id == Event.query.get(event_id).hosted_user_id:
		return redirect(url_for('index'))
	if request.method == 'POST':
		g.user.events.remove(Event.query.get(event_id))
		db.session.commit()
		return redirect(url_for('index'))
	return render_template("remove_event.html",event = Event.query.get(event_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		if not request.form['username']:
			error = 'You have to enter a username'
		elif not request.form['email'] or \
				'@' not in request.form['email']:
			error = 'You have to enter an email address'
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'The two passwords do not match'
		elif get_user_id(request.form['username']) is not None:
			error = 'This username is already taken'
		else:
			db.session.add(User(username=request.form['username'],email=request.form['email'], password_hash=generate_password_hash(request.form['password'])))
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
			session['user_id'] = user.user_id
			return redirect(url_for('index'))
	return render_template('login.html', error=error)


@app.route('/logout')
def logout():
	session.pop('user_id', None)
	return redirect(url_for('index'))