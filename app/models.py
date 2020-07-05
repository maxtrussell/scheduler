from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from app import (
    db,
    login,
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    events = db.relationship(
        'Event',
        backref='owner',
        lazy='dynamic',
        passive_deletes=True,
        cascade="all, delete-orphan",
    )
    commitments = db.relationship(
        'Commitment',
        backref='user',
        lazy='dynamic',
        passive_deletes=True,
        cascade="all, delete-orphan",
    )
    transactions = db.relationship(
        'Transaction',
        backref='user',
        lazy='dynamic',
        passive_deletes=True,
        cascade="all, delete-orphan",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(140), unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    times = db.relationship(
        'Time',
        backref='event',
        lazy='dynamic',
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return '<Event {}>'.format(self.description)

class Time(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id', ondelete='CASCADE'))
    description = db.Column(db.String(140))
    commitments = db.relationship(
        'Commitment',
        backref='time',
        lazy='dynamic',
        cascade="all, delete-orphan",
    )
    __table_args__ = (db.UniqueConstraint('description', 'event_id'),)

    def __repr__(self):
        return '<Time {}>'.format(self.description)

class Commitment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_id = db.Column(db.Integer, db.ForeignKey('time.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    __table_args__ = (db.UniqueConstraint('time_id', 'user_id'),)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(140))
    platinum = db.Column(db.Integer)
    gold = db.Column(db.Integer)
    electrum = db.Column(db.Integer)
    silver = db.Column(db.Integer)
    copper = db.Column(db.Integer)
    __table_args__ = (
        db.CheckConstraint('platinum >= 0', name='platinum_gte_0'),
        db.CheckConstraint('gold >= 0', name='gold_gte_0'),
        db.CheckConstraint('electrum >= 0', name='electrum_gte_0'),
        db.CheckConstraint('silver >= 0', name='silver_gte_0'),
        db.CheckConstraint('copper >= 0', name='copper_gte_0'),
    )

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    description = db.Column(db.String(140))
    platinum = db.Column(db.Integer)
    gold = db.Column(db.Integer)
    electrum = db.Column(db.Integer)
    silver = db.Column(db.Integer)
    copper = db.Column(db.Integer)
    running_total = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

if len(Account.query.all()) == 0:
    a = Account(
        description="Party account",
        platinum=0,
        gold=0,
        electrum=0,
        silver=0,
        copper=0,
    )
    db.session.add(a)
    db.session.commit()
