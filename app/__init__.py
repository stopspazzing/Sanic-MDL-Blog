# app/__init__.py

from sanic import Sanic
app = Sanic(__name__)
from app import views
