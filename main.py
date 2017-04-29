#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from sanic import Sanic
from sanic.exceptions import NotFound
from sanic_useragent import SanicUserAgent
from sanic_compress import Compress
from sanic.response import file, html, redirect
from sanic_session import InMemorySessionInterface
from sanic_jinja2 import SanicJinja2
from sanic_wtf import SanicWTF
from wtforms import StringField, SubmitField, PasswordField, FormField, TextField
from wtforms.validators import DataRequired, Length


app = Sanic(__name__)
jinja = SanicJinja2(app)
Compress(app)
session = InMemorySessionInterface(expiry=600)
SanicUserAgent.init_app(app, default_locale='en_US')
app.config['SECRET_KEY'] = os.urandom(24)

# TODO: Add DB info


@app.middleware('request')
async def add_session_to_request(request):
    await session.open(request)


@app.middleware('response')
async def save_session(request, response):
    await session.save(request, response)


@app.exception(NotFound)
async def ignore_404s(request, exception):
    page = dict()
    page['title'] = '404 Error'
    page['header'] = '404 Error - Page Not Found'
    page['text'] = 'We Can\'t Seem To Find ' + request.url
    return jinja.render('page.html', request, page=page)

wtf = SanicWTF(app)


class LoginForm(wtf.Form):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=3)])
    submit = SubmitField('Sign In')

async def index(request):
    return jinja.render('index.html', request)


async def images(request, name):
    return await file('images/' + name)


async def styles(request):
    return await file('css/styles.css')


async def admin_styles(request):
    return await file('css/admin.css')


async def post(request):
    # TODO: pull values for post from db and add values to post dict
    return jinja.render('post.html', request, postname='Default')


async def dashboard(request):
    cookie_check = request.cookies.get('session')
    if cookie_check is not None:
        return jinja.render('admin.html', request, pagename='Dashboard')
    else:
        return redirect('login')


async def login(request):
    page = dict()
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        get_username = form.username.data
        get_password = form.password.data
        if get_username == "12345" and get_password == "12345":
            request['session']['username'] = get_username
            page['title'] = 'Login'
            page['header'] = 'Thank you for logging in!'
            page['text'] = 'Redirecting in 3 seconds...'
            return jinja.render('page.html', request, page=page,
                                js_head_end='<script defer>window.setTimeout(function(){ window.location = "admin"; },3000);</script>')
    login_check = request['session'].get('username')
    if login_check is None:
        page['title'] = 'Login'
        page['header'] = 'Restricted Area - Login Required'
        return jinja.render('page.html', request, page=page, form=form)
    page['title'] = 'Login'
    page['header'] = 'You\'re already logged in!'
    page['text'] = 'Redirecting in 3 seconds...'
    return jinja.render('page.html', request, page=page,
                        js_head_end='<script defer>window.setTimeout(function(){ window.location = "/"; },3000);</script>')


async def logout(request):
    usr = request['session'].get('username')
    return html(f'<h1>Logging out {usr}</h1>')


async def redirect_index(request):
    return redirect('/')

app.add_route(index, '/')
app.add_route(images, 'images/<name>')
app.add_route(styles, 'styles.css')
app.add_route(admin_styles, 'admin.css')
app.add_route(post, 'post.html')
app.add_route(dashboard, 'admin')
app.add_route(login, 'login', methods=['GET', 'POST'])
app.add_route(logout, 'logout')
app.add_route(redirect_index, '/index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
