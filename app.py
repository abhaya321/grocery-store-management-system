from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from functools import wraps

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL Configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Abhi@1619",
    database="grocery_store2",
    port=3307
)
cursor = db.cursor()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Home route
@app.route('/')
@login_required
def index():
    cursor.execute("""
        SELECT products.id, products.name, products.price, products.stock, categories.name 
        FROM products 
        JOIN categories ON products.category_id = categories.id
    """)
    products = cursor.fetchall()
    return render_template("index.html", products=products)

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash("Username already exists. Please choose another.", "danger")
            return redirect(url_for('signup'))
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        flash("Signup successful. Please log in.", "success")
        return redirect(url_for('login'))
    return render_template("signup.html")

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            session['username'] = username
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials.", "danger")
            return redirect(url_for('login'))
    return render_template("login.html")

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

# Add products
@app.route('/add_products', methods=['GET', 'POST'])
@login_required
def add_products():
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        category_id = request.form['category_id']
        cursor.execute(
            "INSERT INTO products (name, price, stock, category_id) VALUES (%s, %s, %s, %s)",
            (name, price, stock, category_id)
        )
        db.commit()
        flash("Product added successfully!", "success")
        return redirect(url_for('index'))
    return render_template("add_products.html", categories=categories)

# Add order
@app.route('/add_order', methods=['GET', 'POST'])
@login_required
def add_order():
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        if customer_name != session['username']:
            flash("Customer name must match your username.", "danger")
            return render_template("add_order.html", products=products)

        product_ids = request.form.getlist('product_id')
        quantities = request.form.getlist('quantity')

        for pid, qty in zip(product_ids, quantities):
            if pid and qty:
                cursor.execute("SELECT stock FROM products WHERE id = %s", (pid,))
                stock = cursor.fetchone()[0]
                if int(qty) > stock:
                    flash(f"Cannot order {qty} items. Only {stock} in stock for product ID {pid}.", "danger")
                    return render_template("add_order.html", products=products)

        cursor.execute("INSERT INTO orders (customer_name, status) VALUES (%s, 'Placed')", (customer_name,))
        order_id = cursor.lastrowid

        for pid, qty in zip(product_ids, quantities):
            if pid and qty:
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (order_id, pid, qty)
                )
                cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (qty, pid))
        db.commit()
        flash("Order placed successfully!", "success")
        return redirect(url_for('index'))
    return render_template("add_order.html", products=products)

# View orders
@app.route('/orders')
@login_required
def orders():
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    return render_template("view_orders.html", orders=orders)

# Cancel order
@app.route('/cancel_order/<int:order_id>')
@login_required
def cancel_order(order_id):
    cursor.execute("SELECT product_id, quantity FROM order_items WHERE order_id = %s", (order_id,))
    items = cursor.fetchall()

    for pid, qty in items:
        cursor.execute("UPDATE products SET stock = stock + %s WHERE id = %s", (qty, pid))

    cursor.execute("UPDATE orders SET status = 'Cancelled' WHERE id = %s", (order_id,))
    db.commit()
    flash("Order cancelled and stock restored.", "info")
    return redirect(url_for('orders'))

# Delete product
@app.route('/delete_product/<int:id>')
@login_required
def delete_product(id):
    try:
        cursor.execute("DELETE FROM products WHERE id = %s", (id,))
        db.commit()
        flash("Product deleted successfully.", "success")
    except mysql.connector.IntegrityError:
        flash("Cannot delete product. It's linked to existing orders.", "danger")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)