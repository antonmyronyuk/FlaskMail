import hashlib
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(50))
    messages = db.relationship('Message', backref='receiver', lazy='dynamic')

    # call only after adding user email
    def set_token(self):
        self.token = hashlib\
            .md5(bytes(self.email, encoding='utf-8'))\
            .hexdigest() + str(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fields = db.relationship('MessageField', backref='message', lazy='dynamic')

    def get_html(self):
        """
        generate html representation of message
        :return: str
        """
        # print(self.fields.all())

        html = '<br>'.join(
            ['<b>{}:</b> {}'.format(f.field_name, f.field_data)
             for f in self.fields.all()]
        )
        # add time
        html += '<br>received at: <em>{}</em>'.format(self.date)
        return html



class MessageField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    field_name = db.Column(db.Text)
    field_data = db.Column(db.Text)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))
