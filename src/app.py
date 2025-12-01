import os
from flask import Flask
from dotenv import load_dotenv
from models import db

load_dotenv()


def _configure_app(app, test_config):
    if test_config:
        app.config.update(test_config)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL', 'sqlite:///warehouse.db'
        )


def create_app(test_config=None):
    app = Flask(__name__, template_folder='templates')
    _configure_app(app, test_config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

    db.init_app(app)
    # pylint: disable=import-outside-toplevel
    from routes import warehouse_bp
    app.register_blueprint(warehouse_bp)

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    application = create_app()
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    application.run(debug=debug_mode, host='0.0.0.0', port=5000)
