from functools import wraps
from typing import Callable, Any
import os
from flask import Flask, render_template, request, redirect, url_for, make_response, Response
import jwt
from werkzeug.exceptions import HTTPException

import products
from auth import do_login, sign_up
from products import list_products
from cart import add_to_cart as ac, get_cart, remove_from_cart, delete_cart
from checkout import checkout as chk, complete_checkout

app = Flask(__name__)
app.template_folder = 'templates'
SRN = "PES1UG23AM809"

# Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'secret')  # Better to use environment variable
DEBUG_MODE = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'

def require_auth(f: Callable) -> Callable:
    """Decorator to check if user is authenticated"""
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        token = request.cookies.get('token')
        if not token:
            return redirect(url_for('login'))
        try:
            dec = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            kwargs['username'] = dec['sub']
            return f(*args, **kwargs)
        except jwt.InvalidTokenError:
            return redirect(url_for('login'))
    return decorated

@app.route('/')
def index() -> Response:
    return redirect(url_for('browse'))

@app.route('/cart')
@require_auth
def cart(username: str) -> str:
    cart_items = get_cart(username)
    return render_template('cart.jinja', cart=cart_items, srn=SRN)

@app.route('/cart/remove/<int:id>', methods=['POST'])
@require_auth
def remove_cart_item(id: int, username: str) -> Response:
    remove_from_cart(username, id)
    return redirect(url_for('cart'))

@app.route('/cart/delete', methods=['GET'])
@require_auth
def delete_cart_item(username: str) -> Response:
    delete_cart(username)
    return redirect(url_for('cart'))

@app.route('/cart/<int:id>', methods=['POST'])
@require_auth
def add_to_cart(id: int, username: str) -> Response:
    ac(username, id)
    return redirect(url_for('cart'))

@app.route('/product/<int:product_id>')
def product(product_id: int) -> str:
    product_data = products.get_product(product_id)
    return render_template('product_view.jinja', product=product_data, srn=SRN)

@app.route("/product", methods=['GET', 'POST'])
def product_page() -> Any:
    if request.method == 'POST':
        try:
            product_data = {
                "name": request.form['product_name'],
                "cost": float(request.form['product_cost']),
                "qty": int(request.form['product_quantity']),
                "description": request.form['product_description']
            }
            products.add_product(product_data)
            return 'ok'
        except (KeyError, ValueError) as e:
            return str(e), 400
    return render_template('product.jinja', srn=SRN)

@app.route('/login', methods=['GET', 'POST'])
def login() -> Any:
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            token = do_login(username, password)
            response = make_response(redirect(url_for('browse')))
            response.set_cookie('token', token, httponly=True, secure=True)
            return response
        except ValueError as e:
            return {'error': str(e)}, 401
    return render_template('login.jinja', srn=SRN)

@app.route('/register', methods=['GET', 'POST'])
def register() -> Any:
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            sign_up(username, password)
            return redirect(url_for('login'))
        except ValueError as e:
            return {'error': str(e)}, 400
    return render_template('signup.jinja', srn=SRN)

@app.route("/browse")
def browse() -> str:
    return render_template('browse.jinja', items=list_products(), srn=SRN)

@app.route("/checkout", methods=['GET', 'POST'])
@require_auth
def checkout(username: str) -> Any:
    if request.method == 'GET':
        total = chk(username)
        return render_template('checkout.jinja', total=total, srn=SRN)
    return redirect(url_for('browse'))

@app.route("/payment")
@require_auth
def payment(username: str) -> str:
    complete_checkout(username)
    return render_template('payment.jinja', srn=SRN)

@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException) -> Response:
    """Handle HTTP exceptions"""
    return redirect(url_for('login'))

if __name__ == '__main__':
    if SRN[-3:] == "XXX":
        print("Please update your SRN on line 15")
        os._exit(1)
    app.run(debug=DEBUG_MODE)
