#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import urandom, path
import aioodbc
from sanic import Sanic
from sanic.exceptions import NotFound
from sanic.response import file, redirect
from sanic_compress import Compress
from sanic_jinja2 import SanicJinja2
from sanic_session import InMemorySessionInterface
from sanic_useragent import SanicUserAgent
import datetime
from forms import WelcomeForm, DatabaseForm, LoginForm

app = Sanic(__name__)
jinja = SanicJinja2(app)
Compress(app)
session = InMemorySessionInterface(expiry=600)
SanicUserAgent.init_app(app, default_locale='en_US')


@app.listener('before_server_start')
async def setup_cfg(app, loop):
    app.config['SECRET_KEY'] = urandom(24)
    app.config['DEMO_CONTENT'] = True
    try:
        cfg = app.config.from_pyfile('config.py')
        if cfg is None:
            app.config.from_envvar('MY_SETTINGS')
    except FileNotFoundError:
        app.config['DEMO_CONTENT'] = True
        print('Warning - Config Not Found. Using Defaults.')
    if path.isfile('*.db'):
        app.config['SETUP_DB'] = False
        app.config['SETUP_BLOG'] = False
    else:
        app.config['SETUP_DB'] = True
        app.config['SETUP_BLOG'] = True


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
    return jinja.render('page.html', request, page=page)


async def sql_connection():
    try:
        dsn = app.config['DB_URI']
        if not dsn:
            dsn = 'Driver=SQLite3;Database=app.db'
        return await aioodbc.connect(dsn=dsn, loop=app.loop)
    except:
        return False

async def sql_validate():
    if not app.config['DB_TYPE']:
        app.config['DB_TYPE'] = 'sql'
    dbtype = app.config['DB_TYPE']
    if dbtype == 'sql' or None:
        if not app.config['DB_NAME']:
            dbname = 'app.db'
        else:
            dbname = app.config['DB_NAME']
        conn = f'Driver=SQLite3;Database={dbname}'
        try:
            test = await aioodbc.connect(dsn=conn, loop=app.loop)
            if not test:
                return False
            else:
                app.config['DB_URI'] = conn
                return True
        except Exception:
            print('Exception')
            return False
    print('No DB type')
    return False


async def sql_demo():
    con = await sql_connection()
    if app.config['DEMO_CONTENT']:
        await con.execute(
            '''CREATE TABLE "blog_posts" ( `id` INTEGER DEFAULT 'None' PRIMARY KEY AUTOINCREMENT, `post_author` VARCHAR(20) DEFAULT 'Demo', `post_date` DATETIME DEFAULT '0000-00-00 00-00-00', `post_content` TEXT DEFAULT 'None', `post_title` BLOB DEFAULT 'None', `post_name` VARCHAR(200) DEFAULT 'new post', `post_excerpt` TEXT DEFAULT 'None', `post_image` VARCHAR(20) DEFAULT 'road_big.jpg', `post_status` VARCHAR(20) DEFAULT 'publish', `post_modified` DATETIME DEFAULT '0000-00-00 00-00-00', `comment_status` VARCHAR(20) DEFAULT 'open', `post_password` VARCHAR(20) DEFAULT 'None', `post_likes` VARCHAR(20) DEFAULT '0' );''')
        await con.execute(
            '''CREATE TABLE "blog_settings" ( `id` INTEGER DEFAULT 'None', `title` TEXT DEFAULT 'Blog Demo', `created_on` DATETIME DEFAULT '0000-00-00 00-00-00', `username` TEXT DEFAULT 'None', `password` VARCHAR(200) DEFAULT 'publish', `email` VARCHAR(50) DEFAULT 'None', `hidden` TEXT DEFAULT 'True', `https` TEXT DEFAULT 'off', `user_alias` VARCHAR(200) DEFAULT 'Demo', `permalink` TEXT DEFAULT '1', PRIMARY KEY(`id`) );''')
        await con.execute('''INSERT INTO `blog_posts` VALUES (1,'demo','0000-00-00 00-00-00','Excepteur reprehenderit sint exercitation ipsum consequat qui sit id velit elit. Velit anim eiusmod labore sit amet. Voluptate voluptate irure occaecat deserunt incididunt esse in. Sunt velit aliquip sunt elit ex nulla reprehenderit qui ut eiusmod ipsum do. Duis veniam reprehenderit laborum occaecat id proident nulla veniam. Duis enim deserunt voluptate aute veniam sint pariatur exercitation. Irure mollit est sit labore est deserunt pariatur duis aute laboris cupidatat. Consectetur consequat esse est sit veniam adipisicing ipsum enim irure.

<br />

Qui ullamco consectetur aute fugiat officia ullamco proident Lorem ad irure. Sint eu ut consectetur ut esse veniam laboris adipisicing aliquip minim anim labore commodo. Incididunt eu enim enim ipsum Lorem commodo tempor duis eu ullamco tempor elit occaecat sit. Culpa eu sit voluptate ullamco ad irure. Anim commodo aliquip cillum ea nostrud commodo id culpa eu irure ut proident. Incididunt cillum excepteur incididunt mollit exercitation fugiat in. Magna irure laborum amet non ullamco aliqua eu. Aliquip adipisicing dolore irure culpa aute enim. Ullamco quis eiusmod ipsum laboris quis qui.

<br />

Cillum ullamco eu cupidatat excepteur Lorem minim sint quis officia irure irure sint fugiat nostrud. Pariatur Lorem irure excepteur Lorem non irure ea fugiat adipisicing esse nisi ullamco proident sint. Consectetur qui quis cillum occaecat ullamco veniam et Lorem cupidatat pariatur. Labore officia ex aliqua et occaecat velit dolor deserunt minim velit mollit irure. Cillum cupidatat enim officia non velit officia labore. Ut esse nisi voluptate et deserunt enim laborum qui magna sint sunt cillum. Id exercitation labore sint ea labore adipisicing deserunt enim commodo consectetur reprehenderit enim. Est anim nostrud quis non fugiat duis cillum. Aliquip enim officia ad commodo id.','Coffee Pic','coffee-pic','Enim labore aliqua consequat ut quis ad occaecat aliquip incididunt. Sunt nulla eu enim irure enim nostrud aliqua consectetur ad consectetur sunt ullamco officia. Ex officia laborum et consequat duis.','road_big.jpg','publish','0000-00-00 00-00-00','open','None','0');''')
        await con.execute('''INSERT INTO `blog_posts` VALUES (2,'demo','0000-00-00 00-00-00','Excepteur reprehenderit sint exercitation ipsum consequat qui sit id velit elit. Velit anim eiusmod labore sit amet. Voluptate voluptate irure occaecat deserunt incididunt esse in. Sunt velit aliquip sunt elit ex nulla reprehenderit qui ut eiusmod ipsum do. Duis veniam reprehenderit laborum occaecat id proident nulla veniam. Duis enim deserunt voluptate aute veniam sint pariatur exercitation. Irure mollit est sit labore est deserunt pariatur duis aute laboris cupidatat. Consectetur consequat esse est sit veniam adipisicing ipsum enim irure.

<br />

Qui ullamco consectetur aute fugiat officia ullamco proident Lorem ad irure. Sint eu ut consectetur ut esse veniam laboris adipisicing aliquip minim anim labore commodo. Incididunt eu enim enim ipsum Lorem commodo tempor duis eu ullamco tempor elit occaecat sit. Culpa eu sit voluptate ullamco ad irure. Anim commodo aliquip cillum ea nostrud commodo id culpa eu irure ut proident. Incididunt cillum excepteur incididunt mollit exercitation fugiat in. Magna irure laborum amet non ullamco aliqua eu. Aliquip adipisicing dolore irure culpa aute enim. Ullamco quis eiusmod ipsum laboris quis qui.

<br />

Cillum ullamco eu cupidatat excepteur Lorem minim sint quis officia irure irure sint fugiat nostrud. Pariatur Lorem irure excepteur Lorem non irure ea fugiat adipisicing esse nisi ullamco proident sint. Consectetur qui quis cillum occaecat ullamco veniam et Lorem cupidatat pariatur. Labore officia ex aliqua et occaecat velit dolor deserunt minim velit mollit irure. Cillum cupidatat enim officia non velit officia labore. Ut esse nisi voluptate et deserunt enim laborum qui magna sint sunt cillum. Id exercitation labore sint ea labore adipisicing deserunt enim commodo consectetur reprehenderit enim. Est anim nostrud quis non fugiat duis cillum. Aliquip enim officia ad commodo id.','On the road again','on-the-road-again','Enim labore aliqua consequat ut quis ad occaecat aliquip incididunt. Sunt nulla eu enim irure enim nostrud aliqua consectetur ad consectetur sunt ullamco officia. Ex officia laborum et consequat duis.','road_big.jpg','publish','0000-00-00 00-00-00','open','None','0');''')
        await con.execute('''INSERT INTO `blog_posts` VALUES (3,'demo','0000-00-00 00-00-00','Excepteur reprehenderit sint exercitation ipsum consequat qui sit id velit elit. Velit anim eiusmod labore sit amet. Voluptate voluptate irure occaecat deserunt incididunt esse in. Sunt velit aliquip sunt elit ex nulla reprehenderit qui ut eiusmod ipsum do. Duis veniam reprehenderit laborum occaecat id proident nulla veniam. Duis enim deserunt voluptate aute veniam sint pariatur exercitation. Irure mollit est sit labore est deserunt pariatur duis aute laboris cupidatat. Consectetur consequat esse est sit veniam adipisicing ipsum enim irure.

<br />

Qui ullamco consectetur aute fugiat officia ullamco proident Lorem ad irure. Sint eu ut consectetur ut esse veniam laboris adipisicing aliquip minim anim labore commodo. Incididunt eu enim enim ipsum Lorem commodo tempor duis eu ullamco tempor elit occaecat sit. Culpa eu sit voluptate ullamco ad irure. Anim commodo aliquip cillum ea nostrud commodo id culpa eu irure ut proident. Incididunt cillum excepteur incididunt mollit exercitation fugiat in. Magna irure laborum amet non ullamco aliqua eu. Aliquip adipisicing dolore irure culpa aute enim. Ullamco quis eiusmod ipsum laboris quis qui.

<br />

Cillum ullamco eu cupidatat excepteur Lorem minim sint quis officia irure irure sint fugiat nostrud. Pariatur Lorem irure excepteur Lorem non irure ea fugiat adipisicing esse nisi ullamco proident sint. Consectetur qui quis cillum occaecat ullamco veniam et Lorem cupidatat pariatur. Labore officia ex aliqua et occaecat velit dolor deserunt minim velit mollit irure. Cillum cupidatat enim officia non velit officia labore. Ut esse nisi voluptate et deserunt enim laborum qui magna sint sunt cillum. Id exercitation labore sint ea labore adipisicing deserunt enim commodo consectetur reprehenderit enim. Est anim nostrud quis non fugiat duis cillum. Aliquip enim officia ad commodo id.','I couldn’t take any pictures but this was an amazing thing…','i-couldnt-take-any-pictures','Enim labore aliqua consequat ut quis ad occaecat aliquip incididunt. Sunt nulla eu enim irure enim nostrud aliqua consectetur ad consectetur sunt ullamco officia. Ex officia laborum et consequat duis.','road_big.jpg','publish','0000-00-00 00-00-00','open','None','0');''')
        await con.execute('''INSERT INTO `blog_posts` VALUES (4,'demo','0000-00-00 00-00-00','Excepteur reprehenderit sint exercitation ipsum consequat qui sit id velit elit. Velit anim eiusmod labore sit amet. Voluptate voluptate irure occaecat deserunt incididunt esse in. Sunt velit aliquip sunt elit ex nulla reprehenderit qui ut eiusmod ipsum do. Duis veniam reprehenderit laborum occaecat id proident nulla veniam. Duis enim deserunt voluptate aute veniam sint pariatur exercitation. Irure mollit est sit labore est deserunt pariatur duis aute laboris cupidatat. Consectetur consequat esse est sit veniam adipisicing ipsum enim irure.   

<br />

Qui ullamco consectetur aute fugiat officia ullamco proident Lorem ad irure. Sint eu ut consectetur ut esse veniam laboris adipisicing aliquip minim anim labore commodo. Incididunt eu enim enim ipsum Lorem commodo tempor duis eu ullamco tempor elit occaecat sit. Culpa eu sit voluptate ullamco ad irure. Anim commodo aliquip cillum ea nostrud commodo id culpa eu irure ut proident. Incididunt cillum excepteur incididunt mollit exercitation fugiat in. Magna irure laborum amet non ullamco aliqua eu. Aliquip adipisicing dolore irure culpa aute enim. Ullamco quis eiusmod ipsum laboris quis qui.

<br />

Cillum ullamco eu cupidatat excepteur Lorem minim sint quis officia irure irure sint fugiat nostrud. Pariatur Lorem irure excepteur Lorem non irure ea fugiat adipisicing esse nisi ullamco proident sint. Consectetur qui quis cillum occaecat ullamco veniam et Lorem cupidatat pariatur. Labore officia ex aliqua et occaecat velit dolor deserunt minim velit mollit irure. Cillum cupidatat enim officia non velit officia labore. Ut esse nisi voluptate et deserunt enim laborum qui magna sint sunt cillum. Id exercitation labore sint ea labore adipisicing deserunt enim commodo consectetur reprehenderit enim. Est anim nostrud quis non fugiat duis cillum. Aliquip enim officia ad commodo id.','Shopping','shopping','Enim labore aliqua consequat ut quis ad occaecat aliquip incididunt. Sunt nulla eu enim irure enim nostrud aliqua consectetur ad consectetur sunt ullamco officia. Ex officia laborum et consequat duis.','road_big.jpg','publish','0000-00-00 00-00-00','open','None','0');''')
        await con.commit()
    else:
        await con.execute(
            '''CREATE TABLE "blog_posts" ( `id` INTEGER DEFAULT 'None' PRIMARY KEY AUTOINCREMENT, `post_author` VARCHAR(20) DEFAULT 'Demo', `post_date` DATETIME DEFAULT '0000-00-00 00-00-00', `post_content` TEXT DEFAULT 'None', `post_title` BLOB DEFAULT 'None', `post_name` VARCHAR(200) DEFAULT 'new post', `post_excerpt` TEXT DEFAULT 'None', `post_image` VARCHAR(20) DEFAULT 'road_big.jpg', `post_status` VARCHAR(20) DEFAULT 'publish', `post_modified` DATETIME DEFAULT '0000-00-00 00-00-00', `comment_status` VARCHAR(20) DEFAULT 'open', `post_password` VARCHAR(20) DEFAULT 'None', `post_likes` VARCHAR(20) DEFAULT '0' )''')
        await con.execute(
            '''CREATE TABLE "blog_settings" ( `id` INTEGER DEFAULT 'None', `title` TEXT DEFAULT 'Blog Demo', `created_on` DATETIME DEFAULT '0000-00-00 00-00-00', `username` TEXT DEFAULT 'None', `password` VARCHAR(200) DEFAULT 'publish', `email` VARCHAR(50) DEFAULT 'None', `hidden` TEXT DEFAULT 'True', `https` TEXT DEFAULT 'off', `user_alias` VARCHAR(200) DEFAULT 'Demo', `permalink` TEXT DEFAULT '1', PRIMARY KEY(`id`) )''')
        await con.commit()
    # await cur.close()
    await con.close()


async def setup(request):
    page = dict()
    if app.config['SETUP_DB']:
        dform = DatabaseForm(request)
        if request.method == 'POST' and dform.validate():
            app.config['DB_NAME'] = dform.username.data
            app.config['DB_PASSWORD'] = dform.password.data
            app.config['DB_URI'] = dform.host.data
            app.config['DB_TYPE'] = dform.dbtype.data
            valid = await sql_validate()
            if not valid:
                print('Error - DB Not Valid')
                return redirect('setup')
            app.config['SETUP_DB'] = False
            return redirect('setup')
        page['title'] = 'Blog First Start'
        page['header'] = 'Setup Database'
        page['text'] = 'Below you should enter your database connection details.'
        return jinja.render('page.html', request, page=page, form=dform)
    elif app.config['SETUP_BLOG']:
        wform = WelcomeForm(request)
        if request.method == 'POST' and wform.validate():
            # TODO: if valid information, redirect to home, save all created variables from welcome form data to db
            request['session']['username'] = wform.username.data
            app.config['SETUP_BLOG'] = False
            uri = app.config['DB_URI']
            dbt = app.config['DB_TYPE']
            with open("config.py", "wt") as o:
                o.write(f'DB_URI = {repr(uri)}\n')
                o.write(f'DB_TYPE = {repr(dbt)}\n')
                o.write('DEMO_CONTENT = False\n')
            await sql_demo()
            con = await sql_connection()
            date = datetime.datetime.now()
            await con.execute(
                f'INSERT INTO "blog_settings" (`title`,`created_on`,`username`,`password`,`email`,`hidden`) VALUES ("{wform.title.data}","{date}","{wform.username.data}","{wform.password.data}","{wform.email.data}","{wform.seo.data}");')
            await con.commit()
            await con.close()
            return redirect('/')
        page['title'] = 'Blog First Start'
        page['header'] = 'Welcome'
        page['text'] = 'Before you get blogging, we need to setup a few things.'
        return jinja.render('page.html', request, page=page, form=wform)
    page['title'] = 'Setup'
    page['header'] = 'Already Completed'
    page['text'] = 'Redirecting in 3 seconds...'
    return jinja.render('page.html', request, page=page,
                        js_head_end='<script defer>window.setTimeout(function(){ window.location = "/"; }'
                                    ',3000);</script>')


async def index(request):
    con = await sql_connection()
    if not con:
        return redirect('setup')
    cur = await con.cursor()
    await cur.execute('SELECT * FROM blog_posts;')
    fetch = await cur.fetchmany(4)
    if fetch is None:
        page = dict()
        page['post_title'] = 'No Posts Found :('
        page['post_excerpt'] = 'Sorry, We couldn\'t find any posts.'
        return jinja.render('index.html', request, page=page)
    await cur.close()
    await con.close()
    return jinja.render('index.html', request, page=fetch)


async def post(request, name):
    con = await sql_connection()
    if not con:
        return redirect('setup')
    cur = await con.cursor()
    await cur.execute(f'SELECT * FROM blog_posts WHERE post_name="{name}";')
    fetch = await cur.fetchone()
    if not fetch:
        raise NotFound("404 Error", status_code=404)
    await cur.close()
    await con.close()
    return jinja.render('post.html', request, post=fetch)


async def dashboard(request):
    cookie_check = request['session'].get('username')
    if cookie_check is None:
        return redirect('login')
    return jinja.render('admin.html', request, pagename='Dashboard')


async def login(request):
    con = await sql_connection()
    if not con:
        return redirect('setup')
    page = dict()
    lform = LoginForm(request)
    if request.method == 'POST' and lform.validate():
        fuser = lform.username.data
        fpass = lform.password.data
        con = await sql_connection()
        cur = await con.cursor()
        await cur.execute(f'SELECT * FROM "blog_settings" WHERE `username`="{fuser}" AND `password`="{fpass}";')
        usr_pass = await cur.fetchone()
        if usr_pass is not None:
            request['session']['username'] = fuser
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
        return jinja.render('page.html', request, page=page, form=lform,
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


# This is only for testing, nothing useful for average user
async def test(request):
    raise NotFound("Something bad happened", status_code=404)


async def images(request, name):
    return await file('images/' + name)


async def styles(request):
    return await file('css/styles.css')


async def admin_styles(request):
    return await file('css/admin.css')


async def redirect_index(request):
    return redirect('/')


app.add_route(setup, 'setup', methods=['GET', 'POST'])
app.add_route(test, 'test')
app.add_route(index, '/')
app.add_route(images, 'images/<name>')
app.add_route(styles, 'styles.css')
app.add_route(admin_styles, 'admin.css')
app.add_route(post, '/<name>')
app.add_route(dashboard, 'admin')
app.add_route(login, 'login', methods=['GET', 'POST'])
app.add_route(logout, 'logout')
app.add_route(redirect_index, '/index.html')

app.run(host='127.0.0.1', port=8000, debug=True)
