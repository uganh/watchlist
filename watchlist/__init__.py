import os
import sys

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


WIN = sys.platform.startswith('win')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///' if WIN else 'sqlite:////') + \
    os.path.join(app.root_path, os.getenv('DATABASE_FILE', 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    from watchlist.models import User
    return User.query.get(int(user_id))


@app.context_processor
def inject_user():
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user)


from watchlist import commands, errors, views
