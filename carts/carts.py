from flask import Flask, render_template, flash, request, url_for, redirect, session
from content_management import Content
from dbconnect import connection
from forms import AddForm, RegistrationForm, Addproducts, Addproducts_lab
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
from functools import wraps
import gc
from flask_wtf import FlaskForm

TOPIC_DICT = Content()

app = Flask(__name__)

app.secret_key = 'some_secret'

@app.route('/addcart', methods=['POST'])
def AddCart():
    try:
        pass
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)