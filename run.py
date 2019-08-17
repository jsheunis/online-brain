# Run a test server
import config
from openbrain import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host=config.DEFAULT_HOST, port=config.DEFAULT_PORT,
            debug=config.DEBUG, threaded=config.THREADED)
