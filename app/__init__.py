import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.registration_key = os.environ.get('REGISTRATION_KEY') or 'hotlizard14'
app.admins = ['max']
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
migrate.init_app(app, db, render_as_batch=True)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models
