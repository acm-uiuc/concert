import functools
import flask_login
from flask import Flask, Response, request, url_for, render_template, redirect, url_for, current_app, session
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

from concert.models import User
from concert.dbconnector import MongoConnector

ConcertLoginManager = LoginManager()
ConcertDBConnector = MongoConnector()


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return False
        else:
            return f(*args, **kwargs)
    return wrapped

@ConcertLoginManager.user_loader
def load_user(uid):
    res = ConcertDBConnector.get_user_by_id(uid)
    if res == None:
        return None
    newuser = User(res['uid'], res['first_name'], res['last_name'])
    return newuser

