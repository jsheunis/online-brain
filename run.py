# Run a test server
import config
from openbrain import create_app


app = create_app(config.ProductionConfig())

if __name__ == '__main__':
    app.run(host=config.DEFAULT_HOST, port=config.DEFAULT_PORT)
