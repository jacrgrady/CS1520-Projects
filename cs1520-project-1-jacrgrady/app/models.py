from datetime import datetime
from app import db
from hashlib import md5

association_table  = db.Table('association',
	db.Column('userid', db.Integer, db.ForeignKey('user.user_id')),
	db.Column('eventid', db.Integer, db.ForeignKey('event.event_id')))


class User(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True, nullable=False)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128), nullable=False)
	events = db.relationship("Event",
		secondary = association_table,
		backref=db.backref('users', lazy='select')
		,order_by='Event.start_time')
	
	hosted_events = db.relationship('Event', backref='user', lazy=True)
	
	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

	def __repr__(self):
		return '<User {}>'.format(self.username)


class Event(db.Model):
	event_id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(64), nullable=False)
	body = db.Column(db.String(140))
	start_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	end_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)

	hosted_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)

	def __repr__(self):
		return '<Event {}>'.format(self.body)
