from wtforms import Form, BooleanField, TextField, PasswordField, StringField, validators, RadioField, FloatField, IntegerField, TextAreaField

#-------------before 11 April 2020 ----------------------------------
class AddForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    pname = TextField('Name of product', [validators.Length(min=0, max=20)])
    pprice = StringField('Price', [validators.Length(min=0, max=100)])

#----------------- 11 April 2020--------------------------------------
class Addproducts(Form):
    name = StringField('Name', [validators.DataRequired()])
    username = StringField('Username', [validators.DataRequired()])
    price = StringField('Price', [validators.DataRequired()])
    discount = StringField('Discount', default=0)
    stock = StringField('Stock', [validators.DataRequired()])
    discription = StringField('Discription', [validators.DataRequired()])


class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50),validators.Email()])
    password = PasswordField('New Password', [ 
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    role_id=RadioField('Label',choices=[('1','Dental Clinic'),('2','Dental Lab'),('3','Manufacturer')])
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice', [validators.DataRequired()])

# ------------------ 18 April 2020--------------------------------
class Addproducts_lab(Form):
    name = StringField('Name', [validators.DataRequired()])
    username = StringField('Username', [validators.DataRequired()])
    price = StringField('Price', [validators.DataRequired()])
    discount = StringField('Discount', default=0)
    stock = StringField('Stock', [validators.DataRequired()])
    discription = StringField('Discription', [validators.DataRequired()])

    