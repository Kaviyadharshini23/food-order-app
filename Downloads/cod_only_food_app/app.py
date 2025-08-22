from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
import os, json, random, datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SEED_PATH = os.path.join(DATA_DIR, "seed.json")
ORDERS_PATH = os.path.join(DATA_DIR, "orders.json")

def load_seed():
    with open(SEED_PATH, "r") as fh:
        return json.load(fh)

def load_orders():
    if not os.path.exists(ORDERS_PATH):
        with open(ORDERS_PATH, "w") as fh:
            json.dump([], fh)
    with open(ORDERS_PATH, "r") as fh:
        return json.load(fh)

def save_orders(orders):
    with open(ORDERS_PATH, "w") as fh:
        json.dump(orders, fh, indent=2)

def get_cart():
    return session.get("cart", {})  # {item_id: qty}

def set_cart(cart):
    session["cart"] = cart

@app.before_request
def _inject_cart_count():
    cart = get_cart()
    g.cart_count = sum(cart.values())

@app.route("/")
def home():
    data = load_seed()
    restaurants = data.get("restaurants", [])
    return render_template("home.html", restaurants=restaurants, title="Home")

@app.route("/restaurant/<int:restaurant_id>")
def restaurant_menu(restaurant_id):
    data = load_seed()
    restaurant = next((r for r in data["restaurants"] if r["id"] == restaurant_id), None)
    if not restaurant:
        flash("Restaurant not found")
        return redirect(url_for("home"))
    items = [m for m in data["menu_items"] if m["restaurant_id"] == restaurant_id]
    return render_template("menu.html", restaurant=restaurant, items=items, title=restaurant["name"])

@app.post("/add-to-cart")
def add_to_cart():
    item_id = int(request.form.get("item_id"))
    cart = get_cart()
    cart[str(item_id)] = cart.get(str(item_id), 0) + 1
    set_cart(cart)
    flash("Added to cart")
    # Redirect back to referer or home
    return redirect(request.headers.get("Referer", url_for("home")))

@app.get("/cart")
def view_cart():
    data = load_seed()
    cart = get_cart()
    items_lookup = {m["id"]: m for m in data["menu_items"]}
    cart_items = []
    total = 0
    for iid, qty in cart.items():
        item = items_lookup.get(int(iid))
        if item:
            cart_items.append({"item": item, "qty": qty})
            total += item["price"] * qty
    return render_template("cart.html", cart_items=cart_items, total=total, title="Cart")

@app.post("/cart/update")
def update_cart():
    payload = request.get_json(force=True)
    item_id = str(payload.get("item_id"))
    action = payload.get("action")
    cart = get_cart()
    if action == "incr":
        cart[item_id] = cart.get(item_id, 0) + 1
    elif action == "decr":
        if cart.get(item_id, 0) > 1:
            cart[item_id] -= 1
        else:
            cart.pop(item_id, None)
    elif action == "remove":
        cart.pop(item_id, None)
    set_cart(cart)
    return jsonify({"ok": True, "count": sum(cart.values())})

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    data = load_seed()
    cart = get_cart()
    if not cart:
        flash("Your cart is empty.")
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        if not (name and phone and address):
            flash("All fields are required.")
            return redirect(url_for("checkout"))

        # Build order
        items_lookup = {m["id"]: m for m in data["menu_items"]}
        order_items = []
        total = 0
        for iid, qty in cart.items():
            item = items_lookup.get(int(iid))
            if item:
                order_items.append({"id": item["id"], "name": item["name"], "price": item["price"], "qty": qty})
                total += item["price"] * qty

        orders = load_orders()
        order_id = (orders[-1]["id"] + 1) if orders else 1001
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        order = {
            "id": order_id,
            "items": order_items,
            "total": total,
            "payment_method": "COD",
            "status": "Pending",
            "customer": {"name": name, "phone": phone, "address": address},
            "created_at": created_at,
        }
        orders.append(order)
        save_orders(orders)

        # clear cart
        set_cart({})

        # Randomly choose ETA from a restaurant in cart
        eta = random.choice(load_seed()["restaurants"])["eta"]
        return render_template("confirmation.html", order_id=order_id, eta=eta, title="Order Placed")

    return render_template("checkout.html", title="Checkout")

@app.route("/admin/orders", methods=["GET", "POST"])
def admin_orders():
    authed = session.get("admin_authed", False)
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd and pwd == os.environ.get("ADMIN_PASSWORD", "admin123"):
            session["admin_authed"] = True
            authed = True
        else:
            flash("Wrong password")

    orders = load_orders() if authed else []
    return render_template("admin_orders.html", orders=orders, authed=authed, title="Admin: Orders")

if __name__ == "__main__":
    app.run(debug=True)
