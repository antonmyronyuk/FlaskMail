from app import app, mail, db
from flask import render_template, request, url_for, flash, redirect, jsonify
from flask_mail import Message
from sqlalchemy import desc
from smtplib import SMTPException
from werkzeug.datastructures import MultiDict
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm
from app.models import User, Message, MessageField


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template(
        'index.html',
        messages=current_user.messages.order_by(desc(Message.date)),
        checkbox_status=current_user.email_notifications_status()
    )


@app.route('/delete_message/<int:message_id>')
def delete_message(message_id):
    Message.query.filter_by(id=message_id).delete()
    MessageField.query.filter_by(message_id=message_id).delete()
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid email!', 'danger')
            return redirect(url_for('login'))
        if not user.check_password(form.password.data):
            flash('Invalid password!', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        flash('Successfully logged in!', 'success')
        return redirect(next_page)
    return render_template('login.html', title='Log In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Please, log out to register a new account!', 'info')
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        user.set_token()
        db.session.commit()
        flash('You have registered successfully! Please, log in!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Sign up', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('Successfully logged out', 'success')
    return redirect(url_for('login'))


@app.route('/help')
def help_send():
    return render_template('help.html', title='Help')


@app.route('/checker')
def checker():
    return render_template('form.html')


@app.route('/all_users')
def all_users():
    return render_template('all_users.html', users=User.query.all(), title='All users')


@app.route('/flask_send', methods=['POST'])
def flask_send():
    data = request.form
    token = request.args.get('token')
    user = User.query.filter_by(token=token).first()
    if user is None:
        return jsonify({'status': 'Not found'}), 404

    # current message
    message = Message(user_id=user.id)
    db.session.add(message)
    db.session.commit()
    # print('message id = {}'.format(message.id))

    # fill message fields
    for m_name, m_data in data.items():
        field = MessageField(
            field_name=str(m_name),
            field_data=str(m_data),
            message_id=message.id
        )
        db.session.add(field)
    db.session.commit()

    return jsonify({'status': 'OK'}), 200


@app.route('/set_mail_checkbox', methods=['POST'])
def set_mail_checkbox():
    try:
        status = request.form['setter']
    except:
        status = 'off'
    print(status)
    current_user.email_notifications = True if status == 'on' else False
    db.session.commit()
    return redirect(url_for('index'))


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
