from flask import Flask, render_template, url_for

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/my-account')
def account():
    return render_template('account.html')

if __name__ == '__main__':
    app.run()
