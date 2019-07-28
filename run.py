# Run a test server
from openbrain import create_app
import config
import threading

app = create_app()

if __name__=='__main__':
    app.run(host=config.DEFAULT_HOST, port=config.DEFAULT_PORT, 
        debug=config.DEBUG, threaded=config.THREADED)
