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

app = Sanic(__name__)
session = InMemorySessionInterface(expiry=600)
SanicUserAgent.init_app(app, default_locale='en_US')
app.secret_key = os.urandom(24)
Compress(app)
jinja = SanicJinja2(app)


@app.middleware('request')
async def add_session_to_request(request):
    # before each request initialize a session
    # using the client's request session.session_store
    await session.open(request)


@app.middleware('response')
async def save_session(request, response):
    # after each request save the session,
    # pass the response to set client cookies
    await session.save(request, response)


@app.exception(NotFound)
async def ignore_404s(request, exception):
    return jinja.render('page.html', request, pagename='404 Error', pageheader='404 Error - Page Not Found', pagetext='We Can\'t Seem To Find' + request.url)

# Define the handler functions
async def index(request):
    return jinja.render('index.html', request)

async def images(request, name):
    return await file('images/' + name)

async def styles(request):
    return await file('css/styles.css')

async def admin_styles(request):
    return await file('css/admin.css')

async def post(request):
    return jinja.render('post.html', request, postname='Default')

async def dashboard(request):
    cookie_check = request.cookies.get('session')
    if cookie_check is not None:
        return jinja.render('admin.html', request, pagename='Dashboard')
    else:
        return redirect('login')

async def login(request):
    page = dict()
    if request.method == 'POST':
        get_email = request.form.get('email')
        get_password = request.form.get('password')
        if get_email == "12345" and get_password == "12345":
            request['session']['username'] = get_email
            page['title'] = 'Login'
            page['header'] = 'Thank you for logging in!'
            page['text'] = 'Redirecting in 3 seconds...'
            return jinja.render('page.html', request, page=page, js_head_end='<script defer>window.setTimeout(function(){ window.location = "admin"; },3000);</script>')
    cookie_check = request.cookies.get('session')
    # Is cookie set?
    if cookie_check is None:
        page['title'] = 'Login'
        page['header'] = 'Restricted Area - Login Required'
        page['text'] = '<form role="form" novalidate method="POST"><div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label"><input class="mdl-textfield__input" type="email" id="user" name="email"><label class="mdl-textfield__label" for="user">Email address</label></div><div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label"><input class="mdl-textfield__input" type="password" id="password" name="password"><label class="mdl-textfield__label" for="password">Password</label></div><button type="submit" class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored">Login</button></form>'
        # Render generic post and insert login form
        return jinja.render('page.html', request, page=page)
    page['title'] = 'Login'
    page['header'] = 'You\'re already logged in!'
    page['text'] = 'Redirecting in 3 seconds...'
    return jinja.render('page.html', request, page=page, js_head_end='<script defer>window.setTimeout(function(){ window.location = "/"; },3000);</script>')

async def logout(request):
    return html('<h1>Logging out %s</h1>' % request['session'])

async def redirect_index(request):
    return redirect('/')

# Add each handler function as a route
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
