import asyncio
import os
from sanic import Sanic
from sanic_useragent import SanicUserAgent
from sanic_compress import Compress
from sanic.response import text, file, html, redirect
from sanic_session import InMemorySessionInterface

app = Sanic(__name__)
session_interface = InMemorySessionInterface(expiry=600)
SanicUserAgent.init_app(app, default_locale='en_US')
app.secret_key = os.urandom(24)
Compress(app)


@app.middleware('request')
async def add_session_to_request(request):
    # before each request initialize a session
    # using the client's request
    await session_interface.open(request)


@app.middleware('response')
async def save_session(request, response):
    # after each request save the session,
    # pass the response to set client cookies
    await session_interface.save(request, response)

# Define the handler functions
async def index(request):
    return await file('index.html')

async def images(request, name):
    return await file('images\\' + name)

async def styles(request):
    return await file('styles.css')

async def entry(request):
    return await file('entry.html')

async def login(request):
    cookie_check = request.cookies.get('session')
    # Start with html5
    html_code = '<DOCTYPE html>'
    # Add <head>
    html_code += '<head><link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons"><link rel="stylesheet" href="https://code.getmdl.io/1.3.0/material.indigo-pink.min.css"><script defer src="https://code.getmdl.io/1.3.0/material.min.js"></script></head>'
    # Is cookie set?
    h = html(html_code)
    if request.method == 'POST':
        get_email = request.form.get('email')
        get_password = request.form.get('password')
        if get_email == "12345" and get_password == "12345":
            request['session']['username'] = get_email
    if cookie_check is None:
        # Add <body>
        html_code += '<body><h1>Restricted Area - Login Required</h1><br/><form role="form" novalidate action="/form" method="POST"><div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label"><input class="mdl-textfield__input" type="email" id="user" name="email"><label class="mdl-textfield__label" for="user">Email address</label></div><div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label"><input class="mdl-textfield__input" type="password" id="password" name="password"><label class="mdl-textfield__label" for="password">Password</label></div><button type="submit" class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored">Login</button></form></body>'
    else:
        html_code += '<head><script>window.setTimeout(function(){ window.location = "/"; },3000);</script></head><body><h1>Thank you for logging in!</h1><br/><h2>Redirecting in 3 seconds...</h2></body>'
    # Close html5
    html_code += '</html>'
    return h

async def logout(request):
    o = html('<h1>Logging out %s</h1>' % request['session']['username'])
    return o

async def redirect_index(request):
    return redirect('/')

# Add each handler function as a route
app.add_route(index, '/')
app.add_route(images, '/images/<name>')
app.add_route(styles, '/styles.css')
app.add_route(entry, 'entry.html')
app.add_route(login, '/login', methods=['GET', 'POST'])
app.add_route(logout, '/logout')
app.add_route(redirect_index, '/index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
