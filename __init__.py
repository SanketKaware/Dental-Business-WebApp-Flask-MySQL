from flask import Flask, render_template, flash, request, url_for, redirect, session
from content_management import Content
from dbconnect import connection
from wtforms import Form, BooleanField, TextField, PasswordField, validators, RadioField
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
from functools import wraps
import gc
from flask_wtf import FlaskForm



TOPIC_DICT = Content()

app = Flask(__name__)

app.secret_key = 'some_secret'

@app.route('/')
def homepage():
    return render_template("main.html")

@app.route('/dashboard/')
def dashboard():
    # flash("flash test!!!!")
    # flash("fladfasdfsaassh test!!!!")
    # flash("asdfas asfsafs!!!!")
    return render_template("dashboard.html", TOPIC_DICT = TOPIC_DICT)

@app.route('/clinic/')
def clinic():
    return render_template("clinic.html", TOPIC_DICT = TOPIC_DICT)

@app.route('/lab/')
def lab():
    return render_template("lab.html", TOPIC_DICT = TOPIC_DICT)


@app.route('/manufacturer/')
def manufacturer():
    return render_template("manufacturer.html", TOPIC_DICT = TOPIC_DICT)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))
    return wrap

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    # return redirect(url_for('homepage'))
    return redirect(url_for("dashboard"))

@app.route('/login/', methods=["GET","POST"])
def login_page():
    error = ''
    try:
        c, conn = connection()
        if request.method == "POST":

            # data = c.execute("SELECT * FROM users WHERE username = (%s)",
            #                  thwart(request.form['username']))
            
            # data = c.fetchone()[3]

            # if sha256_crypt.verify(request.form['password'], data):
            #     session['logged_in'] = True
            #     session['username'] = request.form['username']

            #     flash("You are now logged in")
            #     # return redirect(url_for("dashboard"))
            #     # return redirect(url_for("clinic"))
            #     # return redirect(url_for("lab"))
            #     return redirect(url_for("manufacturer"))

            # else:
            #     error = "Invalid credentials, try again."
            #-----------------------------------------------------

            if (c.execute("SELECT * FROM users WHERE username = (%s) AND role_id = ('1')",
                              thwart(request.form['username']))):
                data = c.fetchone()[3]
                if sha256_crypt.verify(request.form['password'], data):
                    session['logged_in'] = True
                    session['username'] = request.form['username']
                    flash("You are now logged in")
                    return redirect(url_for("clinic"))
            elif (c.execute("SELECT * FROM users WHERE username = (%s) AND role_id = ('2')",
                              thwart(request.form['username']))):
                data = c.fetchone()[3]
                if sha256_crypt.verify(request.form['password'], data):
                    session['logged_in'] = True
                    session['username'] = request.form['username']
                    flash("You are now logged in")
                    return redirect(url_for("lab"))
            elif (c.execute("SELECT * FROM users WHERE username = (%s) AND role_id = ('3')",
                              thwart(request.form['username']))):
                data = c.fetchone()[3]
                if sha256_crypt.verify(request.form['password'], data):
                    session['logged_in'] = True
                    session['username'] = request.form['username']
                    flash("You are now logged in")
                    return redirect(url_for("manufacturer"))
            else:
                error = "Invalid credentials, try again." 
            #--------------------------------------------------------

        gc.collect()

        return render_template("login.html", error=error)

    except Exception as e:
        #flash(e)
        error = "Invalid credentials, try again."
        return render_template("login.html", error = error)

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    role_id=RadioField('Label',choices=[('1','Dental Clinic'),('2','Dental Lab'),('3','Manufacturer')])
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 21, 2015)', [validators.DataRequired()])
    

@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username  = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            role_id =  form.role_id.data
            c, conn = connection()

            x = c.execute("SELECT * FROM users WHERE username = (%s)",
                          (thwart(username)))

            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                # c.execute("INSERT INTO users (username, password, email, tracking) VALUES (%s, %s, %s, %s)",
                #           (thwart(username), thwart(password), thwart(email), thwart("/introduction-to-python-programming/")))
                c.execute("INSERT INTO users (username, password, email, role_id) VALUES (%s, %s, %s, %s)",
                           (thwart(username), thwart(password), thwart(email), thwart(role_id)))
                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))

        return render_template("register.html", form=form)

    except Exception as e:
        return(str(e))

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=4000)