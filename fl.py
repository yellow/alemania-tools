from flask import Flask, render_template, url_for, redirect, flash, request, jsonify
from forms import RegistrationForm, LoginForm, ProductSearchForm, PostForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt

import os
from datetime import datetime

import stripe

app = Flask(__name__)
app.config['DEBUG'] = True

# secret for form is in environment variable.
app.config['SECRET_KEY'] = os.environ['FORM_CSRF_SECRET']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DB_URI']

app.config['STRIPE_PUBLIC_KEY'] = os.environ['STRIPE_PUBLIC_KEY']
app.config['STRIPE_SECRET_KEY'] = os.environ['STRIPE_SECRET_KEY']
app.config['STRIPE_ENDPOINT_SECRET'] = os.environ['STRIPE_ENDPOINT_SECRET']

stripe.api_key = app.config['STRIPE_SECRET_KEY']

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.firstname}', '{self.email}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    purchase_place = db.Column(db.String(100), nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False)

    failure_description = db.Column(db.Text, nullable=False)
    tag = db.Column(db.String(30))
    quantity = db.Column(db.Integer, default=1)

    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    payment_status = db.Column(db.String(15), nullable=False, default='PENDING')
    stripe_session_id = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"Post('{self.id}', '{self.product.name}', '{self.date_posted}')"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(30), nullable = False)
    price = db.Column(db.Integer, nullable = False)

    description = db.Column(db.Text, nullable=False)

    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

    weight = db.Column(db.String(30), nullable = False)
    dimensions = db.Column(db.String(30), nullable = False)
    sku = db.Column(db.String(30), nullable = False)

    posts = db.relationship('Post', backref='product', lazy=True)

    repairable = db.Column(db.Boolean, nullable = False, default = True)

    stripe_product_id = db.Column(db.String(25), nullable=False)
    stripe_price_id = db.Column(db.String(35), nullable=False)

@app.route('/home')
@app.route('/')
def home():
    print("Path:", request.path)
    print("Endpoint:", request.endpoint)
    return render_template('home.html', title = 'Home')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(firstname=form.firstname.data, lastname=form.lastname.data, 
                email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            flash(f'Hi {user.firstname}! You have successfully logged in.', 'success')
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        flash('You have been logged out.', 'info')
        logout_user()
    return redirect(url_for('home'))

# login required***
@app.route('/tool-selection')
@login_required
def tool_selection():
    form = ProductSearchForm()
    return render_template('tool-selection.html', title = 'Tool Selection', form = form)

@app.route('/product-search', methods = ['POST'])
@login_required
def product_search():
    form = ProductSearchForm()
    if form.validate_on_submit():
        results = Product.query.filter(Product.name.like(f'%{ form.product.data }%')).all()
    return render_template('product_search.html', results = results, product = form.product.data)

@app.route('/product/<int:product_id>', methods = ['GET', 'POST'])
@login_required
def product(product_id):
    prod = Product.query.filter_by(id=product_id).first()
    if not prod:
        return 'Invalid id'

    form = PostForm(quantity = 1)
    if form.validate_on_submit():
        # create stripe session. requires price id of product.
        # redirect to stripe payment page
        session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': prod.stripe_price_id,
                    'quantity': form.quantity.data,
                }],
                mode='payment',
                # is this needed?
                # customer_email=current_user.email,
                success_url=url_for('thanks', _external=True),
                cancel_url=url_for('tool_selection', _external=True, status = 'cancelled')
            )
        new_post = Post(purchase_place=form.place.data,
                purchase_date=form.date.data,
                failure_description=form.description.data,
                tag=form.tag.data,
                quantity=form.quantity.data,
                user_id=current_user.id,
                product_id=prod.id,
                payment_status='PENDING',
                stripe_session_id=session.id
                )
        db.session.add(new_post)
        db.session.commit()
        return redirect(session.url)

    return render_template('product.html', prod = prod, form = form, title = prod.name)

@app.route('/thanks')
@login_required
def thanks():
    return render_template('thanks.html')

# reference:
# https://github.com/PrettyPrinted/youtube_video_code/blob/master/2020/06/12/Accepting%20Payments%20in%20Flask%20Using%20Stripe%20Checkout%20%5B2020%5D/flask_stripe/app.py

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TOO BIG')
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = app.config['STRIPE_ENDPOINT_SECRET']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('INVALID SIGNATURE')
        return {}, 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        completed_post = Post.query.filter_by(stripe_session_id=session['id']).first()
        completed_post.payment_status = 'COMPLETE'
        db.session.commit()
        print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        print(line_items)

    return {}

if __name__ == '__main__':
    app.run(host='0.0.0.0', ssl_context='adhoc')
