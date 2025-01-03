from flask import Flask
from config import Config
from datetime import datetime

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Context Processor
    @app.context_processor
    def utility_processor():
        return {
            'current_year': datetime.now().year
        }

    return app