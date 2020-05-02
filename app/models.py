# app/models.py

# 3rd party imports
from datetime import datetime

import sqlalchemy as sa
from aiomysql.sa import create_engine

# local imports
from app import app

config = app.config

# setup sqlalchemy tables
metadata = sa.MetaData()
tbl = sa.Table('blog_posts', metadata,
               sa.Column('id', sa.Integer(), primary_key=True),
               sa.Column('post_date', sa.DateTime()),
               sa.Column('post_content', sa.String(255)),
               sa.Column('post_title', sa.String(50)),
               sa.Column('post_url', sa.String(30)),
               sa.Column('post_image', sa.String(100)),
               sa.Column('post_status', sa.String(15), default="Draft"),
               sa.Column('post_modified', sa.DateTime()),
               sa.Column('comment_status', sa.String(10)),
               sa.Column('post_password', sa.String(80)),
               sa.Column('post_likes', sa.Integer(), default=0)
               )
tbl2 = sa.Table('blog_settings', metadata,
                sa.Column('id', sa.Integer(), primary_key=True),
                sa.Column('title', sa.String(255), default="My Blog"),
                sa.Column('created_on', sa.DateTime()),
                sa.Column('owner', sa.String(255)),
                sa.Column('seo_hidden', sa.Boolean(), default=True),
                sa.Column('https', sa.Boolean(), default=False),
                sa.Column('short_urls', sa.Boolean(), default=False),
                sa.Column('allow_comments', sa.Boolean(), default=False),
                sa.Column('maintenance_mode', sa.Boolean(), default=False)
                )
tbl3 = sa.Table('blog_users', metadata,
                sa.Column('id', sa.Integer(), primary_key=True),
                sa.Column('username', sa.String(255)),
                sa.Column('created_on', sa.DateTime()),
                sa.Column('email', sa.String(255)),
                sa.Column('password', sa.String(255)),
                sa.Column('user_alias', sa.String(255)),
                sa.Column('public', sa.Boolean(), default=False)
                )


async def sql_master(data):
    e = None
    try:
        dsn = config['DB_URI']
    except Exception as error:
        e = await create_engine(user='root', db='test', host='127.0.0.1', password='1234567890', loop=app.loop)
    # switch one: inserting tables
    # includes setup table creation and demo content
    if len(data) == 5:
        user = data[0]
        password = data[1]
        name = data[2]
        host = data[3]
        dbtype = data[4]
        # validate & create tables
        # testing = True
        # if dbtype == 'sqlite' and not testing:
        #     if not name:
        #         dbse = 'app.db'
        #     else:
        #         dbse = name.join('.db')
        #     config['DB_URI'] = dbse
        #     config['DB_TYPE'] = dbtype
        # elif not testing:
        #     config['DB_URI'] = f'{dbtype}://{user}:{password}@{host}/{name}'
        #     config['DB_TYPE'] = dbtype
        # else:
        #     config['DB_URI'] = 'mysql+pymysql://root:1234567890@localhost:3306/test'
        try:
            async with e.acquire() as con:
                await con.execute(sa.schema.CreateTable(tbl))
                await con.execute(sa.schema.CreateTable(tbl2))
                await con.execute(sa.schema.CreateTable(tbl3))
            e.close()
            await e.wait_closed()
            return True
        except Exception as error:
            print(f'SQL Table Creation Broke! {error}')
            return False
    elif len(data) == 4:
        # finish blog settings
        title = data[0]
        username = data[1]
        password = data[2]
        email = data[3]
        date = datetime.now()
        try:
            ins1 = tbl2.insert()
            ins2 = tbl3.insert()
            async with e.acquire() as con:
                await con.execute(ins1, id=None, title=title, created_on=date, owner=username, seo_hidden=True, https=False, short_urls=False, allow_comments=False, maintenance_mode=False)
                # finish blog users
                await con.execute(ins2, id=None, username=username, created_on=date, email=email, password=password, user_alias='', public=False)
            e.close()
            await e.wait_closed()
            return True
        except Exception as error:
            print(f'SQL Blog Settings Table Creation Broke! {error}')
            return False
    #switch two: selecting tables
        #includes selecting tables for posts (such as front page) and search
    # e = await create_engine(dsn)
    # e = await create_engine(user='root', db='test', host='127.0.0.1', password='1234567890', loop=app.loop)
    elif len(data) == 2:
        query = data[0]
        count = data[1]
        if query is None:
            s = sa.select(tbl)
        else:
            s = sa.select(tbl).where(tbl.c.post_title == query)
        try:
            async with e.acquire() as con:
                await con.execute(s)
                if count == 'all':
                    val = await con.fetch()
                    e.close()
                    await e.wait_closed()
                    return val
                if count == 1:
                    val = await con.fetchone()
                    e.close()
                    await e.wait_closed()
                    return val
                if count > 1:
                    val = await con.fetchmany(count)
                    e.close()
                    await e.wait_closed()
                    return val
        except Exception as error:
            print(f'SQL Selection Broke! {error}')
            return False
        e.close()
        await e.wait_closed()
    else:
        return False


async def sql_demo():
    try:
        e = await create_engine(user='root', db='test', host='127.0.0.1', password='1234567890', loop=app.loop)
        async with e.acquire() as con:
            await con.execute(tbl.insert().values(post_date='0000-00-00 00-00-00',
                                                  post_content='Qui ullamco consectetur aute fugiat officia ullamco proident Lorem ad irure. Sint eu ut consectetur ut esse veniam laboris adipisicing aliquip minim anim labore commodo. Incididunt eu enim enim ipsum Lorem commodo tempor duis eu ullamco tempor elit occaecat sit. Culpa eu sit voluptate ullamco ad irure. Anim commodo aliquip cillum ea nostrud commodo id culpa eu irure ut proident. Incididunt cillum excepteur incididunt mollit exercitation fugiat in. Magna irure laborum amet non ullamco aliqua eu. Aliquip adipisicing dolore irure culpa aute enim. Ullamco quis eiusmod ipsum laboris quis qui.',
                                                  post_title='Coffee Pic', post_url='coffee-pic',
                                                  post_image='coffee.jpg', post_status='publish',
                                                  post_modified='0000-00-00 00-00-00', comment_status='open',
                                                  post_password='None'))
            # if config['DEMO_CONTENT']:
            #     await con.execute('''INSERT INTO "blog_posts" VALUES (2,'demo','0000-00-00 00-00-00','Excepteur reprehenderit sint exercitation ipsum consequat qui sit id velit elit. Velit anim eiusmod labore sit amet. Voluptate voluptate irure occaecat deserunt incididunt esse in. Sunt velit aliquip sunt elit ex nulla reprehenderit qui ut eiusmod ipsum do. Duis veniam reprehenderit laborum occaecat id proident nulla veniam. Duis enim deserunt voluptate aute veniam sint pariatur exercitation. Irure mollit est sit labore est deserunt pariatur duis aute laboris cupidatat. Consectetur consequat esse est sit veniam adipisicing ipsum enim irure.','On the road again','on-the-road-again','road.jpg','publish','0000-00-00 00-00-00','open','None','0');''')
            #     await con.execute('''INSERT INTO "blog_posts" VALUES (3,'demo','0000-00-00 00-00-00','Cillum ullamco eu cupidatat excepteur Lorem minim sint quis officia irure irure sint fugiat nostrud. Pariatur Lorem irure excepteur Lorem non irure ea fugiat adipisicing esse nisi ullamco proident sint. Consectetur qui quis cillum occaecat ullamco veniam et Lorem cupidatat pariatur. Labore officia ex aliqua et occaecat velit dolor deserunt minim velit mollit irure. Cillum cupidatat enim officia non velit officia labore. Ut esse nisi voluptate et deserunt enim laborum qui magna sint sunt cillum. Id exercitation labore sint ea labore adipisicing deserunt enim commodo consectetur reprehenderit enim. Est anim nostrud quis non fugiat duis cillum. Aliquip enim officia ad commodo id.','I couldn’t take any pictures but this was an amazing thing…','i-couldnt-take-any-pictures','road_big.jpg','publish','0000-00-00 00-00-00','open','None','0');''')
            #     await con.execute('''INSERT INTO "blog_posts" VALUES (4,'demo','0000-00-00 00-00-00','Cillum ullamco eu cupidatat excepteur Lorem minim sint quis officia irure irure sint fugiat nostrud. Pariatur Lorem irure excepteur Lorem non irure ea fugiat adipisicing esse nisi ullamco proident sint. Consectetur qui quis cillum occaecat ullamco veniam et Lorem cupidatat pariatur. Labore officia ex aliqua et occaecat velit dolor deserunt minim velit mollit irure. Cillum cupidatat enim officia non velit officia labore. Ut esse nisi voluptate et deserunt enim laborum qui magna sint sunt cillum. Id exercitation labore sint ea labore adipisicing deserunt enim commodo consectetur reprehenderit enim. Est anim nostrud quis non fugiat duis cillum. Aliquip enim officia ad commodo id.','Shopping','shopping','shopping.jpg','publish','0000-00-00 00-00-00','open','None','0');''')
            e.close()
            await e.wait_closed()
    except Exception as error:
        print(f'SQL Demo Broke! {error}')
        return False
