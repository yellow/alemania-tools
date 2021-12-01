from flask import Flask, render_template, url_for, redirect, flash, request
from forms import RegistrationForm, LoginForm

import os

app = Flask(__name__)
app.config['DEBUG'] = True

# secret for form is in environment variable.
app.config['SECRET_KEY'] = os.environ['FORM_CSRF_SECRET']

@app.route('/')
def home():
    print("Path:", request.path)
    print("Endpoint:", request.endpoint)
    return render_template('home.html', title = 'Home')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))#, xyzzy = 'spoon'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/tool-selection')
def tool_selection():
    return render_template('tool-selection.html', title = 'Tool Selection')

@app.route('/cart')
def cart():
    return render_template('cart.html', title = 'My Cart')

if __name__ == '__main__':
    app.run()
