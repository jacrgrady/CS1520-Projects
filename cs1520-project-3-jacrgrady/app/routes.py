import sys

from app import app, users,rooms,chatRoom,chatMessage,Object
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack,jsonify
import json


@app.before_request
def before_request():
	g.user = None
	g.room = None
	if 'user' in session:
		g.user = session['user']
		try:
			g.room = session['room']
		except KeyError:
			g.room = None

#helper function to get room given the name
def getRoom(chat_id):
	return next((x for x in rooms if x.name == chat_id), None)

@app.route('/')
@app.route('/index')
def index():
	session['room'] = None
	g.room = session['room']
	return render_template('index.html', user = g.user, rooms = rooms,error=None)

#This is for users that were kicked from their room
@app.route('/index/error')
def indexError():
	session['room'] = None
	g.room = session['room']
	return render_template('index.html', user = g.user, rooms = rooms,error="The room you were in was deleted")

@app.route("/createRoom", methods=['GET', 'POST'])
def createRoom():
	error = ""
	if request.method == 'POST':
		room_name = request.form['name']
		if getRoom(room_name) is not None:
			error = "Please make a unique room name"
		elif room_name:
			room = chatRoom(g.user,room_name)
			rooms.append(room)
			return redirect(url_for('index')) 
	return render_template('createRoom.html',user = g.user, rooms = rooms,error=error)

@app.route("/chat/<chat_id>")
def chat(chat_id):
	session['room'] = chat_id.replace("%20"," ")
	g.room = session['room']
	return render_template('chat.html', user = g.user,chat=getRoom(g.room), rooms = rooms)#TODO


@app.route('/login', methods=['GET', 'POST'])
def login():
	error = ""
	if request.method == 'POST':
		user_login = request.form['username']
		password_login = request.form['password']
		if not user_login:
			error = "You have to enter a username"
		elif not password_login:
			error = "You have to enter a password"
		elif user_login not in users:
			error = "This user does not exist. Please <a href="+url_for('signup')+">sign up</a>"
		elif password_login != users[user_login]:
			error = "Wrong username/password"
		else:
			session['user'] = user_login
			session['room'] = None
			return redirect(url_for('index')) 
	return render_template('login.html', error=error)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
	error = ""
	if request.method == 'POST':
		if not request.form['username']:
			error = "You have to enter a username"
		elif not request.form['password']:
			error = "You have to enter a password"
		elif request.form['username'] in users:
			error = "This user already exists"
		else:
			users[request.form['username']] = request.form['username']
			return redirect(url_for('index'))
	return render_template('signup.html', error=error)

@app.route("/logout", methods=['GET', 'POST'])
def logout():
	session.pop('user', None)
	return redirect(url_for('index'))


@app.route("/new_item", methods=["POST"])
def add():
	room_id = g.room
	for index, item in enumerate(rooms):
		if item.name == room_id:
			rooms[index].messages.append(chatMessage(author=g.user,message=request.form["newChat"]))
			return "OK!"
	return 400

@app.route("/items/<chatNumber>")
def get_items(chatNumber):
	room_id = g.room
	for index, item in enumerate(rooms):
	    if item.name == room_id:
	        return rooms[index].getNewChats(chatNumber = int(chatNumber)) 
	return json.dumps({"error":"Room does not exist"})#TODO

@app.route("/rooms")
def getRooms():
	if g.room is not None and not getRoom(g.room):
		return json.dumps({"error":"Room does not exist"})
	roomJSON = Object()
	roomList = []
	for room in rooms:
		me = Object()
		me.name = room.name
		roomList.append(me)
	roomJSON.rooms = roomList
	return roomJSON.toJSON()

@app.route("/deleteRoom", methods=["POST"])
def deleteRoom():
	room_id = g.room
	for index, item in enumerate(rooms):
		if item.name == room_id:
			rooms.pop(index)
			return "OK!"
	return 400