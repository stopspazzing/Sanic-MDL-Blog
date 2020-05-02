# app/views.py

# native imports
import datetime
from os import urandom, path

# 3rd party imports
from sanic.exceptions import NotFound
from sanic.response import redirect
from sanic_compress import Compress
from sanic_jinja2 import SanicJinja2
from sanic_session import InMemorySessionInterface
from sanic_useragent import SanicUserAgent
from sanic_auth import Auth, User

# local imports
from app import app
from app.forms import WelcomeForm, DatabaseForm, LoginForm
from app.models import sql_master

# initialize imports
Compress(app)
SanicUserAgent.init_app(app, default_locale='en_US')
jinja = SanicJinja2(app)
config = app.config
jrender = jinja.render
session = InMemorySessionInterface(expiry=600)
config['AUTH_LOGIN_ENDPOINT'] = 'login'


@app.listener('before_server_start')
async def setup_cfg(app, loop):
    config['SECRET_KEY'] = urandom(24)
    config['DEMO_CONTENT'] = True
    if path.isfile('*.db'):
        config['SETUP_DB'] = False
        config['SETUP_BLOG'] = False
    else:
        config['SETUP_DB'] = True
        config['SETUP_BLOG'] = True
    try:
        cfg = config.from_pyfile('config.py')
        if cfg is None:
            config.from_envvar('MY_SETTINGS')
        print('Successfully imported config.')
    except FileNotFoundError:
        config['DEMO_CONTENT'] = True
        print('Warning - Config Not Found. Using Defaults.')


@app.listener('after_server_start')
async def notify_server_started(app, loop):
    print('Server successfully started.')


@app.listener('before_server_stop')
async def notify_server_stopping(app, loop):
    print('Server shutting down...')


@app.listener('after_server_stop')
async def close_db(app, loop):
    print('Server successfully shutdown.')


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
    return jrender('page.html', request, page=page)

auth = Auth(app)


async def setup(request):
    page = dict()
    if config['SETUP_DB']:
        dform = DatabaseForm(request)
        if request.method == 'POST' and dform.validate():
            print('Setting up DB')
            data = (dform.user.data, dform.password.data, dform.name.data, dform.host.data, dform.type.data)
            await sql_master(data)
            # if not valid:
            #     print('Error - DB Not Valid')
            #     return redirect(app.url_for('setup'))
            config['SETUP_DB'] = False
            print('DB Setup Finished')
            return redirect(app.url_for('setup'))
        page['title'] = 'Blog First Start'
        page['header'] = 'Setup Database'
        page['text'] = 'Below you should enter your database connection details.'
        return jrender('page.html', request, page=page, form=dform)
    elif config['SETUP_BLOG']:
        print('Setting up Blog')
        wform = WelcomeForm(request)
        if request.method == 'POST' and wform.validate():
            user = User(id=1, name=wform.username.data)
            auth.login_user(request, user)
            # uri = config['DB_URI']
            # dbt = config['DB_TYPE']
            # with open("config.py", "wt") as o:
            #     o.write(f'DB_URI = {repr(uri)}\n')
            #     o.write(f'DB_TYPE = {repr(dbt)}\n')
            #     o.write('DEMO_CONTENT = False\n')
            #     o.write('SETUP_DB = False\n')
            #     o.write('SETUP_BLOG = False\n')
            # print('Wrote config.py')
            # demo = await sql_demo()
            # print('Injected Demo Content')
            # if not demo:
            #     print('Demo content broke')
            #     return redirect(app.url_for('setup'))
            # print('Finished With Demo Content')
            data = (wform.title.data, wform.username.data, wform.password.data, wform.email.data)
            finish_up = await sql_master(data)
            if not finish_up:
                return redirect(app.url_for('setup'))
            config['SETUP_BLOG'] = False
            return redirect('/')
        page['title'] = 'Blog First Start'
        page['header'] = 'Welcome'
        page['text'] = 'Before you get blogging, we need to setup a few things.'
        return jrender('page.html', request, page=page, form=wform)
    page['title'] = 'Setup'
    page['header'] = 'Already Completed'
    page['text'] = 'Redirecting in 3 seconds...'
    return jrender('page.html', request, page=page,
                   js_head_end='<script defer>window.setTimeout(function(){ window.location = "/"; },3000);</script>')


async def index(request):
    data = (None, 4)
    try:
        fetch = await sql_master(data)
        if fetch is None:
            page = dict()
            page['header'] = 'No Posts Found :('
            page['text'] = 'Sorry, We couldn\'t find any posts.'
            return jrender('page.html', request, page=page)
        return jrender('index.html', request, page=fetch)
    except Exception as error:
        print(f'Index Request Broke! {error}')
        raise NotFound("404 Error", status_code=404)


async def post(request, name):
    data = (f'SELECT * FROM blog_posts WHERE post_name="{name}";', 1)
    try:
        fetch = await sql_master(data)
        if not fetch:
            raise NotFound("404 Error", status_code=404)
        return jrender('post.html', request, post=fetch)
    except Exception as error:
        print(f'Post Broke! {error}')
        raise NotFound("404 Error", status_code=404)


@auth.login_required
async def dashboard(request):
    return jrender('admin.html', request, pagename='Dashboard')


async def login(request):
    page = dict()
    lform = LoginForm(request)
    if request.method == 'POST' and lform.validate():
        fuser = lform.username.data
        fpass = lform.password.data
        data = (f'SELECT * FROM "blog_users" WHERE `username`="{fuser}" AND `password`="{fpass}";', 1)
        fetch = await sql_master(data)
        if fetch is not None:
            user = User(id=1, name=fuser)
            auth.login_user(request, user)
            page['title'] = 'Login'
            page['header'] = 'Thank you for logging in!'
            page['text'] = 'Redirecting in 3 seconds...'
            return jrender('page.html', request, page=page,
                           js_head_end='<script defer>window.setTimeout(function(){ window.location = "admin"; },3000);'
                                       '</script>')
        else:
            page['error'] = 'Login Failed. Please Try Again.'
    login_check = request['session'].get('username')
    if login_check is None:
        page['title'] = 'Login'
        page['header'] = 'Restricted Area - Login Required'
        return jrender('page.html', request, page=page, form=lform,
                       css_head_end='<style>.mdl-layout{align-items: center;justify-content: center;}'
                                    '.mdl-layout__content {padding: 24px;flex: none;}</style>')
    page['title'] = 'Login'
    page['header'] = 'You\'re already logged in!'
    page['text'] = 'Redirecting in 3 seconds...'
    return jrender('page.html', request, page=page,
                   js_head_end='<script defer>window.setTimeout(function(){ window.location = "admin"; },3000);'
                               '</script>')


@auth.login_required
async def logout(request):
    page = dict()
    auth.logout_user(request)
    page['title'] = 'Logging Out'
    page['header'] = 'You have been successfully logged out'
    page['text'] = 'Redirecting in 3 seconds...'
    return jrender('page.html', request, page=page,
                   js_head_end='<script defer>window.setTimeout(function(){ window.location = "/"; },3000);</script>')


async def redirect_index(request):
    return redirect('/')

# Static Files
app.static('images/', './app/static/images/')
app.static('css/', './app/static/css/')

# Routes
app.add_route(setup, 'setup', methods=['GET', 'POST'])
app.add_route(index, '/')
app.add_route(post, '/<name>')
app.add_route(dashboard, 'admin')
app.add_route(login, 'login', methods=['GET', 'POST'])
app.add_route(logout, 'logout')
app.add_route(redirect_index, '/index.html')
