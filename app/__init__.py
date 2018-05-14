import logging
from logging.handlers import SMTPHandler

from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from config import Config


login = LoginManager()
login.login_view = 'auth.login'
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    mail_handler = SMTPHandler(
        mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
        fromaddr=app.config['MAIL_DEFAULT_SENDER'],
        toaddrs=app.config['RECIPIENTS'], subject='FLASK_MS Failure',
        credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']),
        secure=()
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))

    if not app.debug:
        app.logger.addHandler(mail_handler)
        logging.getLogger('werkzeug').addHandler(mail_handler)

    app.logger.info('Server startup')

    return app

from app import models
