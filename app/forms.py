from sanic_wtf import SanicForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length, Email, InputRequired


class LoginForm(SanicForm):
    """
    Admin Login Form
    """
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Sign In')


class WelcomeForm(SanicForm):
    """
    Setup Blog Form
    """
    title = StringField('Site Title', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('New Password',
                             validators=[DataRequired(), EqualTo('confirm', message='Passwords must match'),
                                         Length(min=5, max=25, message='Password needs to be 5-25 characters long.')])
    confirm = PasswordField('Repeat Password')
    email = StringField('Your E-mail', validators=[DataRequired(), Email(message='Invalid Email')])
    seo = BooleanField('Hide website from search engines?', validators=[DataRequired()])
    submit = SubmitField('Install')


class DatabaseForm(SanicForm):
    """
    Setup Database Form
    """
    type = SelectField('Database Type', choices=[('sql', 'SQLite'), ('post', 'Postgres'), ('mysql', 'MySQL')])
    name = StringField('Database Name')
    user = StringField('Username')
    password = PasswordField('Password')
    host = StringField('Host')
    submit = SubmitField('Submit')
