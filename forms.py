# reference https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog
# the above repository is MIT Licensed so no worries.

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    firstname = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ProductSearchForm(FlaskForm):
    product = StringField('Product', validators=[DataRequired(), Length(min=2, max=20)])
    search = SubmitField('Search')

class PostForm(FlaskForm):
    place = StringField('Place of Purchase', validators=[DataRequired(), Length(min=2, max=20)])
    date = DateField('Date of Purchase', validators=[DataRequired()])
    description = StringField('Description of Failure', validators=[DataRequired(), Length(min=5)])
    tag = StringField('Customer Tool Reference/Tag')

    tos = BooleanField('Do you accept the ToS?', validators=[DataRequired()])

    submit = SubmitField('Submit')
