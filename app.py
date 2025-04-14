from flask import Flask
from flask_restful import Api
from scripts.cli_commands import (init_db_command, generate_data_command)
from resource.routes import reg_resources, api_bp
from database.models import db
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    api = Api(app)
    reg_resources(api)
    app.config.from_object(config_class)
    db.init_app(app)
    app.register_blueprint(api_bp)
    app.cli.add_command(init_db_command)
    app.cli.add_command(generate_data_command)
    return app

if __name__ == '__main__': #pragma: no cover
    flask_app = create_app()
    flask_app.run(debug=True)
