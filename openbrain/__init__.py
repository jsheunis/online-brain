from flask import Flask
from . import file_monitor

import threading
from .cache import cache


def create_app(configObject):
    """
    Application factory method
    """

    app = Flask(__name__)

    app.config.from_object(configObject)

    # Initialize application extensions
    from openbrain.models import db
    from openbrain.common import migrate

    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)

    # Register the app blueprints
    from openbrain.settings.views import settings_bp
    from openbrain.visualization.views import visualization_bp
    from openbrain.plotting.views import plotting_bp

    app.register_blueprint(settings_bp)
    app.register_blueprint(visualization_bp)
    app.register_blueprint(plotting_bp)

    # Run file system monitor in a new thread
    fs_thread = threading.Thread(target=file_monitor.run)
    fs_thread.daemon = True
    fs_thread.start()

    return app
