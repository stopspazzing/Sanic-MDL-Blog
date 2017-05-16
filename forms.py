from sanic_wtf import SanicForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, EqualTo


class LoginForm(SanicForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class WelcomeForm(SanicForm):
    title = StringField('Site Title', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('New Password',
                             validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    email = StringField('Your E-mail', validators=[DataRequired()])
    seo = BooleanField('Hide website from search engines?', validators=[DataRequired()])
    submit = SubmitField('Install')


class DatabaseForm(SanicForm):
    dbtype = SelectField('Database Type', choices=[('sql', 'SQLite'), ('post', 'Postgres'), ('mysql', 'MySQL')])
    database = StringField('Database Name')
    username = StringField('Username')
    password = PasswordField('Password')
    host = StringField('Host')
    submit = SubmitField('Submit')
