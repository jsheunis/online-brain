from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from . import file_monitor

import config
import threading
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

    # Run file system watcher
    fs_thread = threading.Thread(target=file_monitor.run)
    fs_thread.daemon = True
    fs_thread.start()
    
    return app
