from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import config

migrate = Migrate()


def create_app():
    app = Flask(__name__)    
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    from openbrain.models import db
    db.init_app(app)
    migrate.init_app(app, db)

    from openbrain.visualization.views import visualization_bp
    app.register_blueprint(visualization_bp)

    return app
