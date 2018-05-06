from threading import Thread

from flask import current_app
from flask_mail import Message as FlaskMessage

from app import mail
from app.models import User, Message


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(user: User, message: Message):
    app = current_app._get_current_object()
    print(app.config['MAIL_DEFAULT_SENDER'])
    msg = FlaskMessage(
        subject='FlaskMail',
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email]
    )
    msg.html = message.get_html()
    Thread(target=send_async_email, args=(app, msg)).start()
