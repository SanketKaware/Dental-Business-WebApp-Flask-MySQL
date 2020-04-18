from flask import redirect, render_template, url_for, flash, request
from dbconnect import connection
# from Dental1 import app
# from .models import Addproduct
from .forms import Addproducts


@app.route('/addproduct', methods=['GET','POST'])
def addproduct():
    try:
        form = Addproducts(request.form)

        if request.method=="POST" in form.validate():
            name = form.name.data
            price = form.price.data
            discount = form.discount.data
            stock = form.stock.data
            desc = form.discription.data

            c.execute("INSERT INTO products_manufacturer1 (name, price, discount, stock, desc) VALUES (%s, %s, %s, %s, %s)",
                        (thwart(name), thwart(price), thwart(discount), thwart(stock), thwart(desc)))
            conn.commit()
            flash(f'The product {name} was added in database','success')
            c.close()
            conn.close()
            gc.collect()

            return redirect(url_for('manufacturer'))
        return render_template('products/addproduct.html', form=form, title='Add a Product')

    except Exception as e:
        return(str(e))

