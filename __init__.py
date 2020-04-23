from flask import Flask, render_template, flash, request, url_for, redirect, session
from content_management import Content
from dbconnect import connection
from forms import AddForm, RegistrationForm, Addproducts, Addproducts_lab
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
from functools import wraps
import gc
from flask_wtf import FlaskForm
from carts.carts import  AddCart


TOPIC_DICT = Content()

app = Flask(__name__)

app.secret_key = 'some_secret'

@app.route('/')
def homepage():
    return render_template("main.html")

@app.route('/dashboard/')
def dashboard():
    return render_template("dashboard.html", TOPIC_DICT = TOPIC_DICT)
#-----------------------------------------------------------------------------------
def MagerDicts(dict1,dict2):
    if isinstance(dict1, list) and isinstance(dict2,list):
        return dict1  + dict2
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))


#--------------------------------------AddCart for Clinic->Details->Add Cart------------------------------------------------
@app.route('/addcart', methods=['POST'])
def AddCart():
    try:
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        c, conn = connection()
        data = c.execute("SELECT * FROM products_lab WHERE id= %s",product_id)
        products1 = c.fetchone()
        if request.method == "POST":
            DictItems = {product_id:{'name':products1[1], 'price':products1[3], 'discount': products1[4], 'quantity':quantity}}
            print(product_id, quantity)
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    print('This  product is already addded in your cart')
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] = item['quantity'] + 1
                else:
                    session['Shoppingcart'] = MagerDicts(session['Shoppingcart'], DictItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)
              
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)



@app.route('/carts', methods=['GET'])
def getCart():
    if 'Shoppingcart'not in session or len(session['Shoppingcart'])<=0:
        c, conn = connection()
        if (c.execute("SELECT * FROM users WHERE role_id = ('1')")):
            session['logged_in'] = True
            return redirect(url_for("clinic"))
    
        elif (c.execute("SELECT * FROM users WHERE role_id = ('2')")):
            session['logged_in'] = True
            return redirect(url_for("lab"))

        elif (c.execute("SELECT * FROM users WHERE role_id = ('3')")):
            session['logged_in'] = True
            return redirect(url_for("manufacturer"))

    subtotal = 0
    grandtotal = 0 
    for key, product in session['Shoppingcart'].items():
        discount = (product['discount']/100) * float(product['price'])
        subtotal += float(product['price']) * int(product['quantity'])
        subtotal -= discount
        tax = ("%0.2f" % (.06 * float(subtotal)))
        grandtotal = float("%.2f" % (1.06 * subtotal))

    return render_template('products/carts.html', tax=tax, grandtotal=grandtotal)



@app.route('/updatecart/<int:code>', methods=['POST'])
def updatecart(code):
    if 'Shoppingcart'not in session or len(session['Shoppingcart']) <= 0:
        return redirect('carts')

    if request.method == "POST":
        quantity = request.form.get('quantity')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['quantity'] = quantity
                    flash('Item is updated')
                    return redirect(url_for('getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('getCart'))



@app.route('/deleteitem/<int:id>', methods=['GET'])
def deleteitem(id):
    if 'Shoppingcart'not in session or len(session['Shoppingcart']) <= 0:
        c, conn = connection()
        if (c.execute("SELECT * FROM users WHERE role_id = ('1')")):
            if 'logged_in' in session:
                session['logged_in'] = True
            return redirect(url_for("clinic"))
    
        elif (c.execute("SELECT * FROM users WHERE role_id = ('2')")):
            session['logged_in'] = True
            return redirect(url_for("lab"))

        elif (c.execute("SELECT * FROM users WHERE role_id = ('3')")):
            session['logged_in'] = True
            return redirect(url_for("manufacturer"))

        # return redirect('carts')
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('getCart'))

@app.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart', None)
        return redirect('carts')
    except Exception as e:
        print(e)



@app.route('/empty')
def empty_cart():
    try:
        session.clear()
        return redirect(url_for('carts'))
    except Exception as e:
        print(e)

#--------------------------------------AddCart for Lab->Details->Add Cart------------------------------------------------
@app.route('/addcart_lab', methods=['POST'])
def AddCart_lab():
    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        c, conn = connection()
        data = c.execute("SELECT * FROM products_manufacturer1 WHERE id= %s",product_id)
        products1 = c.fetchone()
        if request.method == "POST":
            DictItems = {product_id:{'name':products1[1], 'price':products1[3], 'discount': products1[4], 'quantity':quantity}}
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += 1
                else:
                    session['Shoppingcart'] = MagerDicts(session['Shoppingcart'], DictItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)
              
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)
#--------------------------------------------------------------------------------------
@app.route('/clinic/')
def clinic():
    page = request.args.get('page',1, type=int)
    per_page = 4
    c, conn = connection()
    data = c.execute("SELECT * FROM products_lab where stock>0 order by name, price DESC LIMIT 10 offset 0")
    # data = c.execute("SELECT * FROM products_lab order by name, price DESC LIMIT 10 offset 0")
    products1 = c.fetchall()
    # products1.paginate(page=page, per_page=4)
    # products1.paginate(page=page, per_page=4)
    # data1 = c.execute("SELECT DISTINCT username FROM products_lab")
    # sellers1 = c.fetchall()
    # print(products1)
    return render_template("clinic.html", products=products1, TOPIC_DICT = TOPIC_DICT)
    # return render_template("clinic.html", TOPIC_DICT = TOPIC_DICT)
#----------------------------Singel_page for Clinic->Details->Details info page for clinic----------------------------------------------------------
@app.route('/products/<int:id>')
def single_page(id):
    c, conn = connection()
    data = c.execute("SELECT * FROM products_lab WHERE id= %s",id)
    products1 = c.fetchall()
    return render_template('products/single_page.html', products=products1)
#----------------------------Singel_page for Lab->Details->Details info page for Lab----------------------------------------------------------
@app.route('/products1/<int:id>')
def detail_page(id):
    c, conn = connection()
    data = c.execute("SELECT * FROM products_manufacturer1 WHERE id= %s",id)
    products1 = c.fetchall()
    return render_template('products/detail_page.html', products=products1)

# @app.route('/sellers/')
# def get_sellers():   
#     c, conn = connection()
#     data = c.execute("SELECT DISTINCT username FROM products_lab")
#     sellers = c.fetchall()
#     # print(products1)
#     return render_template("clinic.html", sellers=sellers,TOPIC_DICT = TOPIC_DICT)

# @app.route('/addproduct_lab/', methods=['GET','POST'])
# def addproduct_lab():
#     try:
#         form = Addproducts_lab(request.form)

#         if request.method=="POST" and form.validate():
#             name = form.name.data
#             username = form.username.data
#             price = form.price.data
#             discount = form.discount.data
#             stock = form.stock.data
#             discription = form.discription.data
#             c, conn = connection()

#             c.execute("INSERT INTO products_lab (name, username, price, discount, stock, discription) VALUES (%s, %s, %s, %s, %s, %s)",
#                         (thwart(name), thwart(username), thwart(price), thwart(discount), thwart(stock), thwart(discription)))
#             conn.commit()
#             flash(f'The product {name} was added in database','success')
#             c.close()
#             conn.close()
#             gc.collect()

#             return redirect(url_for('lab'))
#         return render_template('products/addproduct_lab.html', form=form, title='Add a Product')
#     except Exception as e:
#         return(str(e))

# @app.route('/updateproduct_lab/<int:id>', methods=['GET','POST'])
# def updateproduct_lab(id):
#     form = Addproducts_lab(request.form)
#     return render_template('products/updateproduct_lab.html',  form=form, product = record, title='Update a Product')

# @app.route('/deleteproduct_lab/<int:id>', methods=['POST'])
# def deleteproduct_lab(id):
#     try:
#         product = Addproducts_lab(request.form)
        
#         if request.method=="POST":
#             name = product.name.data                    # April 17,2020.- Delete button working properly but this name parameter is not passing value in {name} and also print(record) is not working
#             c, conn = connection()
#             print("Displaying Manufacturer products Before Deleting it")
#             c.execute("DELETE FROM products_lab WHERE id= %s",id)
#             record = c.fetchone()
#             print(record)
#             conn.commit()
#             flash(f'The product {name} was deleted from your record','success')
#             c.close()
#             conn.close()
#             gc.collect()
#             return redirect(url_for('lab'))
#     except Exception as e:
#         return(str(e))
#--------------------------------------------------------------------------------------

@app.route('/lab/')
def lab():
    c, conn = connection()
    data = c.execute("SELECT * FROM products_manufacturer1 order by name, price DESC")
    products1 = c.fetchall()
    # print(products1)
    return render_template("lab.html", products=products1, TOPIC_DICT = TOPIC_DICT)



@app.route('/products/<int:id>')
def single_page1(id):
    c, conn = connection()
    data = c.execute("SELECT * FROM products_lab WHERE id= %s",id)
    products1 = c.fetchall()
    return render_template('products/single_page.html', products=products1)

@app.route('/labproduct/')
def labproduct():
    c, conn = connection()
    data = c.execute("SELECT * FROM products_lab order by name, price DESC")
    products1 = c.fetchall()
    # print(products1)
    return render_template("products/labproduct.html", products=products1, TOPIC_DICT = TOPIC_DICT)

@app.route('/addproduct_lab/', methods=['GET','POST'])
def addproduct_lab():
    try:
        form = Addproducts_lab(request.form)

        if request.method=="POST" and form.validate():
            name = form.name.data
            username = form.username.data
            price = form.price.data
            discount = form.discount.data
            stock = form.stock.data
            discription = form.discription.data
            c, conn = connection()

            c.execute("INSERT INTO products_lab (name, username, price, discount, stock, discription) VALUES (%s, %s, %s, %s, %s, %s)",
                        (thwart(name), thwart(username), thwart(price), thwart(discount), thwart(stock), thwart(discription)))
            conn.commit()
            flash(f'The product {name} was added in database','success')
            c.close()
            conn.close()
            gc.collect()

            return redirect(url_for('lab'))
        return render_template('products/addproduct_lab.html', form=form, title='Add a Product')
    except Exception as e:
        return(str(e))

@app.route('/updateproduct_lab/<int:id>', methods=['GET','POST'])
def updateproduct_lab(id):
    form = Addproducts_lab(request.form)
    return render_template('products/updateproduct_lab.html',  form=form, product = record, title='Update a Product')

@app.route('/deleteproduct_lab/<int:id>', methods=['POST'])
def deleteproduct_lab(id):
    try:
        product = Addproducts_lab(request.form)
        
        if request.method=="POST":
            name = product.name.data                    # April 17,2020.- Delete button working properly but this name parameter is not passing value in {name} and also print(record) is not working
            c, conn = connection()
            print("Displaying Manufacturer products Before Deleting it")
            c.execute("DELETE FROM products_lab WHERE id= %s",id)
            record = c.fetchone()
            print(record)
            conn.commit()
            flash(f'The product {name} was deleted from your record','success')
            c.close()
            conn.close()
            gc.collect()
            return redirect(url_for('lab'))
    except Exception as e:
        return(str(e))
#--------------------------------------------------------------------------------------

@app.route('/manufacturer/')
def manufacturer():
    c, conn = connection()
    data = c.execute("SELECT * FROM products_manufacturer1 order by name, price DESC")
    products1 = c.fetchall()
    # print(products1)
    return render_template("manufacturer.html", products=products1)

#-------------------------11 April 2020 start -----------------------
@app.route('/addproduct/', methods=['GET','POST'])
def addproduct():
    try:
        form = Addproducts(request.form)

        if request.method=="POST" and form.validate():
            name = form.name.data
            username = form.username.data
            price = form.price.data
            discount = form.discount.data
            stock = form.stock.data
            discription = form.discription.data
            c, conn = connection()

            c.execute("INSERT INTO products_manufacturer1 (name, username, price, discount, stock, discription) VALUES (%s, %s, %s, %s, %s, %s)",
                        (thwart(name), thwart(username), thwart(price), thwart(discount), thwart(stock), thwart(discription)))
            conn.commit()
            flash(f'The product {name} was added in database','success')
            c.close()
            conn.close()
            gc.collect()

            return redirect(url_for('manufacturer'))
        return render_template('products/addproduct.html', form=form, title='Add a Product')
    except Exception as e:
        return(str(e))
#-------------------------17 April 2020 START -----------------------
@app.route('/updateproduct/<int:id>', methods=['GET','POST'])
def updateproduct(id):
    try:
        form = Addproducts(request.form)
        record = None
        # print(id=%s, id)
        
        # if request.method=="POST":
        if request.method=="POST" and form.validate():
            c, conn = connection()
            # c.execute("UPDATE products_manufacturer1 SET name = %s, username = %s, price = %s, discount = %s, stock = %s, discription = %s WHERE id = %s",
            #     form.name.data,
            #     form.username.data,
            #     form.price.data,
            #     form.discount.data,
            #     form.stock.data,
            #     form.discription.data,
            #     id)
            c.execute("UPDATE products_manufacturer1 SET (name, username, price, discount, stock, discription) WHERE id = %s VALUES (%s, %s, %s, %s, %s, %s)",
                id,
                form.name.data,
                form.username.data,
                form.price.data,
                form.discount.data,
                form.stock.data,
                form.discription.data,
                )
            # c.execute("UPDATE products_manufacturer1 SET name = %s, username = %s, price = %s, discount = %s, stock = %s, discription = %s WHERE id = %s",
            #      (thwart(name), thwart(username), thwart(price), thwart(discount), thwart(stock), thwart(discription), id))
            record = c.fetchone()
            print(record)
            conn.commit()
            flash(f'The product {name} was updated in database','success')
            c.close()
            conn.close()
            gc.collect()
            return redirect(url_for('manufacturer'))

        # else:
        # # if request.method=="GET":
        #     c, conn = connection()
        #     # product = c.execute("SELECT * FROM products_manufacturer1 where id = %s", id)
        #     c.execute("SELECT * FROM products_manufacturer1 where id = %s", id)
        #     product1 = c.fetchone()
        #     print(product1)
        #     conn.commit()
        #     c.close()
        #     conn.close()
        #     gc.collect()
        # form.name.data = product1[1]
        # form.username.data = product1[2]
        # form.price.data = product1[3]
        # form.discount.data = product1[4]
        # form.stock.data = product1[5]
        # form.discription.data = product1[6]
        # return render_template('products/updateproduct.html', id= id, form=form, title='Update a Product')
        return render_template('products/updateproduct.html',  form=form, product = record, title='Update a Product')
    except Exception as e:
        return(str(e))

#--------------------- 17 April 2020----------------------------
@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
    try:
        product = Addproducts(request.form)
        
        if request.method=="POST":
            name = product.name.data                    # April 17,2020.- Delete button working properly but this name parameter is not passing value in {name} and also print(record) is not working
            c, conn = connection()
            print("Displaying Manufacturer products Before Deleting it")
            c.execute("DELETE FROM products_manufacturer1 WHERE id= %s",id)
            record = c.fetchone()
            print(record)
            conn.commit()
            flash(f'The product {name} was deleted from your record','success')
            c.close()
            conn.close()
            gc.collect()
            return redirect(url_for('manufacturer'))
    except Exception as e:
        return(str(e))
#--------------------------------------------------------------------------------------

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
                else:
                    flash('Wrong password, please try again later', 'danger')
            elif (c.execute("SELECT * FROM users WHERE username = (%s) AND role_id = ('2')",
                              thwart(request.form['username']))):
                data = c.fetchone()[3]
                if sha256_crypt.verify(request.form['password'], data):
                    session['logged_in'] = True
                    session['username'] = request.form['username']
                    flash("You are now logged in")
                    return redirect(url_for("lab"))
                else:
                    flash('Wrong password, please try again later', 'danger')
            elif (c.execute("SELECT * FROM users WHERE username = (%s) AND role_id = ('3')",
                              thwart(request.form['username']))):
                data = c.fetchone()[3]
                if sha256_crypt.verify(request.form['password'], data):
                    session['logged_in'] = True
                    session['username'] = request.form['username']
                    flash("You are now logged in")
                    return redirect(url_for("manufacturer"))
                else:
                    flash('Wrong password, please try again later', 'danger')
            else:
                error = "Invalid credentials, try again." 
            #--------------------------------------------------------

        gc.collect()

        return render_template("login.html", error=error)

    except Exception as e:
        #flash(e)
        error = "Invalid credentials, try again."
        return render_template("login.html", error = error)

# class RegistrationForm(Form):
#     username = TextField('Username', [validators.Length(min=4, max=20)])
#     email = TextField('Email Address', [validators.Length(min=6, max=50),validators.Email()])
#     password = PasswordField('New Password', [ 
#         validators.DataRequired(),
#         validators.EqualTo('confirm', message='Passwords must match')
#     ])
#     confirm = PasswordField('Repeat Password')
#     role_id=RadioField('Label',choices=[('1','Dental Clinic'),('2','Dental Lab'),('3','Manufacturer')])
#     accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 21, 2015)', [validators.DataRequired()])
    

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
                flash(f'Welcome {form.username.data} '"Thanks for registering!",'success')
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