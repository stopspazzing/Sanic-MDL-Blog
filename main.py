#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import aioodbc
from sanic import Sanic
from sanic.exceptions import NotFound
from sanic.response import file, redirect
from sanic_compress import Compress
from sanic_jinja2 import SanicJinja2
from sanic_session import InMemorySessionInterface
from sanic_useragent import SanicUserAgent
from sanic_wtf import SanicForm
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
    app.config['DEMO_CONTENT'] = True
    app.config['DATABASE'] = 'Driver=SQLite;Database=data.db'
    try:
        cfg = app.config.from_pyfile('config.cfg')
        if cfg is None:
            app.config.from_envvar('config_file')
    except FileNotFoundError:
        print('Error - Config Not Found')
    await db_setup()


@app.listener('after_server_start')
async def notify_server_started(app, loop):
    print('Server successfully started!')


@app.listener('before_server_stop')
async def notify_server_stopping(app, loop):
    print('Server shutting down!')


@app.listener('after_server_stop')
async def close_db(app, loop):
    conn = await db_connection()
    await conn.close()


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


class LoginForm(SanicForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


async def db_connection():
    if app.config['DATABASE']:
        dsn = app.config['DATABASE']  # needs to be the actual config for dsn pulled from config db
    else:
        dsn = 'Driver=SQLite;Database=data.db'
    return await aioodbc.connect(dsn=dsn, loop=app.loop)


async def db_setup():
    conn = await db_connection()
    cur = await conn.cursor()
    await cur.execute('CREATE TABLE blog_data (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL default \'None\', post_author UNSIGNED BIG INT(20) NOT NULL default \'0\', post_date DATETIME NOT NULL default \'0000-00-00 00-00-00\', post_content TEXT NOT NULL default \'None\', post_title TEXT NOT NULL default \'None\', post_excerpt TEXT NOT NULL default \'None\', post_status VARCHAR(20) NOT NULL default \'publish\', post_modified DATETIME NOT NULL, comment_status VARCHAR(20) NOT NULL default \'open\', post_password VARCHAR(20) NOT NULL, post_name VARCHAR(200) NOT NULL, post_likes VARCHAR(20) NOT NULL)')
    if app.config['DEMO_CONTENT']:
        await cur.execute('CREATE TABLE blog_demo (ID INTEGER NOT NULL DEFAULT \'None\' PRIMARY KEY AUTOINCREMENT, post_author VARCHAR(20) NOT NULL DEFAULT \'demo\', post_date DATETIME NOT NULL DEFAULT \'0000-00-00 00-00-00\', post_content TEXT NOT NULL DEFAULT \'None\', post_title TEXT NOT NULL DEFAULT \'None\', post_name VARCHAR(200) NOT NULL DEFAULT \'new post\', post_excerpt TEXT NOT NULL DEFAULT \'None\', post_image VARCHAR(20) DEFAULT \'road_big.jpg\', post_status VARCHAR(20) NOT NULL DEFAULT \'publish\', post_modified DATETIME NOT NULL DEFAULT \'0000-00-00 00-00-00\', comment_status VARCHAR(20) NOT NULL DEFAULT \'open\', post_password VARCHAR(20) NOT NULL DEFAULT \'None\', post_likes VARCHAR(20) NOT NULL DEFAULT \'0\' )')
    data = await cur.fetchone()
    if data is None:
        print('this db is empty yo')
    else:
        print('this db isn\'t empty bro')
    await cur.close()
    await conn.close()


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
    form = LoginForm(request)
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


async def test(request):
    conn = await db_connection()
    cur = await conn.cursor()
    data = await cur.execute('SELECT * FROM blog_demo ORDER BY ID;')
    for d in data:
        print(d)
    await cur.close()
    await conn.close()


async def redirect_index(request):
    return redirect('/')

app.add_route(test, 'test')
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
