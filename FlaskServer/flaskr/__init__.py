import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# create and configure the app
from .config import Config

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config())

app.config.from_mapping(
    # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
)

# Initialize database
db = SQLAlchemy()
db.init_app(app)

# Register blueprints
from . import auth
app.register_blueprint(auth.bp)
