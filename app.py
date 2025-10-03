from flask import Flask, render_template, url_for, abort, request, flash, redirect
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flash messages

PRODUCTS = [
    {
        "id": 1,
        "slug": "ayurvedic-hair-oil-200ml",
        "title": "Ayurvedic Herbal Enriched Hair Oil",
        "subtitle": "Strengthens | Nourishes | Promotes Growth",
        "qty": "200ml",
        "price": 750,
        "mrp": "₹750",
        "best_before": "12 months",
        "image": "hairoil.JPG",
        "ingredients": ["Amla","Shallots","Aloe Vera","Hibiscus","Neem","Henna","Curry Leaves"],
        "directions": "Warm a small amount of oil and gently massage into the scalp..."
    },
    {
        "id": 2,
        "slug": "nalangu-maavu-100g",
        "title": "Nalangu Maavu",
        "subtitle": "27 Herbal Bath Powder",
        "qty": "100gm",
        "price": 399,
        "mrp": "₹399",
        "best_before": "6 months",
        "image": "label4.JPG",
        "ingredients": [],
        "directions": "Take the required amount of Nalangu Maavu in a bowl..."
    },
    {
        "id": 3,
        "slug": "organic-shikakai-200g",
        "title": "Organic Shikakai Powder",
        "subtitle": "",
        "qty": "200gm",
        "price": 699,
        "mrp": "₹699",
        "best_before": "6 months",
        "image": "sikakai.JPG",
        "ingredients": [],
        "directions": "Natural Bloom Organic Shikakai Powder has been used in India for centuries..."
    }
]

ORDERS = []  # store buyers' info temporarily

# --- Simple Admin Credentials ---
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"


def get_image_filename(image):
    if image.lower().endswith('.jpg'):
        return image[:-4] + '.JPG'
    return image

@app.context_processor
def utility_processor():
    return dict(get_image_filename=get_image_filename)

@app.route("/")
def home():
    return render_template("home.html", products=PRODUCTS)

@app.route("/products")
def products():
    return render_template("products.html", products=PRODUCTS)

@app.route("/product/<slug>")
def product_detail(slug):
    prod = next((p for p in PRODUCTS if p["slug"] == slug), None)
    if not prod:
        abort(404)
    return render_template("product_detail.html", product=prod)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        user_info = {
            "name": request.form['name'],
            "address": request.form['address'],
            "phone": request.form['phone'],
            "email": request.form['email']
        }
        # Save order in memory
        ORDERS.append(user_info)
        flash('Order placed successfully!', 'success')
        return render_template('confirmation.html', user_info=user_info, seller_info={
            "name": "Natural Bloom",
            "address": "194, Sri Sakthi Nagar, Gandhinagar post, Kurinjipadi Taluk, Cuddalore - 607308",
            "phone": "+91-7449299859",
            "email": "naturalbloomcare@hotmail.com"
        })
    return render_template('checkout.html')
@app.route('/other-works')
def other_works():
    return render_template('other_works.html')  # your Zeenat Mam page

@app.route("/about")
def about():
    return render_template("about.html")

# ADMIN SECTION
# -----------------------

# Login
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["admin_logged_in"] = True
            flash("Welcome, Admin!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials!", "danger")
            return redirect(url_for("admin_login"))

    return render_template("admin_login.html")

# Logout
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("admin_login"))

# Protect routes
def admin_required(func):
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("You must log in first.", "warning")
            return redirect(url_for("admin_login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__  # keep function name
    return wrapper

@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html", products=PRODUCTS, orders=ORDERS)

@app.route("/admin/add", methods=["GET", "POST"])
@admin_required
def admin_add_product():
    if request.method == "POST":
        new_id = len(PRODUCTS) + 1
        slug = request.form["slug"]
        product = {
            "id": new_id,
            "slug": slug,
            "title": request.form["title"],
            "subtitle": request.form.get("subtitle", ""),
            "qty": request.form["qty"],
            "price": float(request.form["price"]),
            "mrp": f"₹{request.form['price']}",
            "best_before": request.form.get("best_before", ""),
            "image": request.form.get("image", "label3.JPG"),
            "ingredients": request.form.get("ingredients", "").split(","),
            "directions": request.form.get("directions", "")
        }
        PRODUCTS.append(product)
        flash("Product added successfully!", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_add_product.html")
@app.route("/admin/edit/<int:product_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_product(product_id):
    # Find the product
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        # Update product fields
        product["title"] = request.form["title"]
        product["subtitle"] = request.form.get("subtitle", "")
        product["qty"] = request.form["qty"]
        product["price"] = float(request.form["price"])
        product["mrp"] = f"₹{request.form['price']}"
        product["best_before"] = request.form.get("best_before", "")
        product["image"] = request.form.get("image", product["image"])
        product["ingredients"] = request.form.get("ingredients", "").split(",")
        product["directions"] = request.form.get("directions", product.get("directions", ""))

        flash(f'Product "{product["title"]}" updated successfully!', "success")
        return redirect(url_for("admin_dashboard"))

    # Render pre-filled edit form
    return render_template("admin_edit_product.html", product=product)

@app.route("/admin/delete/<int:product_id>")
@admin_required
def admin_delete_product(product_id):
    global PRODUCTS
    # Find the product
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for("admin_dashboard"))
    
    # Remove product
    PRODUCTS = [p for p in PRODUCTS if p["id"] != product_id]
    flash(f'Product "{product["title"]}" deleted successfully!', "success")
    return redirect(url_for("admin_dashboard"))  # <-- must return a response
@app.route('/admin/delete_order/<int:order_id>')
def admin_delete_order(order_id):
    # Fetch the order by ID
    order = Order.query.get_or_404(order_id)

    # Delete the order from the database
    db.session.delete(order)
    db.session.commit()

    # Optional: flash a message
    flash("Order marked as delivered and removed!", "success")

    # Redirect back to the admin dashboard
    return redirect(url_for('admin_dashboard'))

if __name__ == "__main__":
    app.run(debug=True)
