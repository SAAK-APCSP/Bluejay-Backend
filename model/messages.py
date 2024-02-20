from random import randrange
from datetime import date
import os, base64
import json

from __init__ import app, db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

class Message(db.Model):
    __tablename__ = 'messages'  # table name is plural, class name is singular

    # Define the Message schema with "vars" from object
    id = db.Column(db.Integer, primary_key=True)
    _uid = db.Column(db.String(255), unique=False, nullable=False)
    _message = db.Column(db.Text, nullable=False)
    _date = db.Column(db.DateTime, nullable=False, default=date.today())
    _likes = db.Column(db.Integer, nullable=False, default=0)
    
    # constructor of a Message object, initializes the instance variables within object (self)
    def __init__(self, uid, message, likes, date=date.today()):
        self._uid = uid
        self._message = message
        self._date = date
        self._likes = likes

    # a uid getter method, extracts uid from object
    @property
    def uid(self):
        return self._uid
    
    # a setter function, allows uid to be updated after initial object creation
    @uid.setter
    def is_uid(self, uid):
        self._uid = uid

    # a message getter method, extracts message from object
    @property
    def message(self):
        return self._message
    
    # a setter function, allows message to be updated after initial object creation
    @message.setter
    def message(self, message):
        self._message = message
    
    # a date getter method, extracts date from object
    @property
    def date(self):
        return self._date.strftime('%m-%d-%Y %H:%M:%S')
    
    @property
    def likes(self):
        return self._likes
    
    @likes.setter
    def likes(self, likes):
        self._likes = likes
        db.session.commit()
    
    # date should have a setter method as well if needed for updates
    