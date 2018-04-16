from app import app, mail
from flask import render_template, request, url_for, flash
from flask_mail import Message
from smtplib import SMTPException
from werkzeug.datastructures import MultiDict


@app.route('/')
@app.route('/index')
def index():
    return render_template('form.html')


@app.route('/help')
def help_send():
    return render_template('help.html')


@app.route('/send', methods=['POST'])
def send():
    data = MultiDict(request.form)
    del data['receiver']

    # make message text
    text = '<br>'.join(['<b>{}:</b> {}'.format(n, t) for n, t in data.items()])

    msg = Message(
        'FlaskMail',
        recipients=[request.form['receiver']],
        html=text
    )
    try:
        with app.app_context():
            mail.send(msg)
    except SMTPException as e:
        return str(e), 500

    return 'Success', 200
