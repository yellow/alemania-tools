from flask import Flask, render_template, url_for

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/my-account')
def account():
    return render_template('account.html')

@app.route('/tool-selection')
def tool_selection():
    return render_template('tool-selection.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

if __name__ == '__main__':
    app.run()
