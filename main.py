#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from sanic import Sanic
from sanic.exceptions import NotFound
from sanic_useragent import SanicUserAgent
from sanic_compress import Compress
from sanic.response import file, redirect
from sanic_session import InMemorySessionInterface
from sanic_jinja2 import SanicJinja2
from sanic_wtf import SanicWTF
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

app = Sanic(__name__)
jinja = SanicJinja2(app)
Compress(app)
session = InMemorySessionInterface(expiry=600)
SanicUserAgent.init_app(app, default_locale='en_US')


@app.listener('before_server_start')
async def setup_cfg(app, loop):
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['DATABASE'] = 'database.db'
    app.config['DEMO_CONTENT'] = True
    try:
        cfg = app.config.from_pyfile('config.cfg')
        if cfg is None:
            app.config.from_envvar('config_file')
    except FileNotFoundError:
        print('Error - Config Not Found')
    app.db = sqlite3.connect(app.config['DATABASE'])
    app.db.execute(
        '''CREATE TABLE IF NOT EXISTS blog_data(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL default 'None', post_author UNSIGNED BIG INT(20) NOT NULL default '0', post_date DATETIME NOT NULL default '0000-00-00 00-00-00', post_content TEXT NOT NULL default 'None', post_title TEXT NOT NULL default 'None', post_excerpt TEXT NOT NULL default 'None', post_status VARCHAR(20) NOT NULL default 'publish', post_modified DATETIME NOT NULL, comment_status VARCHAR(20) NOT NULL default 'open', post_password VARCHAR(20) NOT NULL, post_name VARCHAR(200) NOT NULL, post_likes VARCHAR(20) NOT NULL)''')
    if app.config['DEMO_CONTENT']:
        app.db.execute(
            '''CREATE TABLE IF NOT EXISTS blog_demo(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL default 'None', post_author VARCHAR(20) NOT NULL default 'demo', post_date DATETIME NOT NULL default '0000-00-00 00-00-00', post_content TEXT NOT NULL default 'None', post_title TEXT NOT NULL default 'None', post_excerpt TEXT NOT NULL default 'None', post_status VARCHAR(20) NOT NULL default 'publish', post_modified DATETIME NOT NULL default '0000-00-00 00-00-00', comment_status VARCHAR(20) NOT NULL default 'open', post_password VARCHAR(20) NOT NULL default 'None', post_name VARCHAR(200) NOT NULL default 'new post', post_likes VARCHAR(20) default '0')''')
        #app.db.cursor().execute('''INSERT INTO blog_demo (post_author,post_date,post_content,post_title,post_excerpt,post_name,post_likes) VALUES ('demo','2017-05-02 14:38:12.228329','this is test content filler for your enjoyment','test','this is test content filler...','test','2');''')


@app.listener('after_server_start')
async def notify_server_started(app, loop):
    print('Server successfully started!')


@app.listener('before_server_stop')
async def notify_server_stopping(app, loop):
    print('Server shutting down!')


@app.listener('after_server_stop')
async def close_db(app, loop):
    app.db.close()


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
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

async def index(request):
    # TODO: Need to pull posts and their excerpts then order them by date
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
    cookie_check = request['session'].get('username')
    if cookie_check is None:
        return redirect('login')
    return jinja.render('admin.html', request, pagename='Dashboard')


async def login(request):
    page = dict()
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        get_user = form.username.data
        get_pass = form.password.data
        # TODO: Get username and password from db to verify against
        if get_user == "12345" and get_pass == "12345":
            request['session']['username'] = get_user
            page['title'] = 'Login'
            page['header'] = 'Thank you for logging in!'
            page['text'] = 'Redirecting in 3 seconds...'
            return jinja.render('page.html', request, page=page,
                                js_head_end='<script defer>window.setTimeout(function(){ window.location = "admin"; }'
                                            ',3000);</script>')
    login_check = request['session'].get('username')
    if login_check is None:
        page['title'] = 'Login'
        page['header'] = 'Restricted Area - Login Required'
        return jinja.render('page.html', request, page=page, form=form,
                            css_head_end='<style>.mdl-layout{align-items: center;justify-content: center;}'
                                         '.mdl-layout__content {padding: 24px;flex: none;}</style>')
    page['title'] = 'Login'
    page['header'] = 'You\'re already logged in!'
    page['text'] = 'Redirecting in 3 seconds...'
    return jinja.render('page.html', request, page=page,
                        js_head_end='<script defer>window.setTimeout(function(){ window.location = "admin"; },3000);'
                                    '</script>')


async def logout(request):
    page = dict()
    del request['session']['username']
    page['title'] = 'Logging Out'
    page['header'] = 'You have been successfully logged out'
    page['text'] = 'Redirecting in 3 seconds...'
    return jinja.render('page.html', request, page=page,
                        js_head_end='<script defer>window.setTimeout(function(){ window.location = "/"; }'
                                    ',3000);</script>')


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
