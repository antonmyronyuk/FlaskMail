from app import app, mail, db
from flask import render_template, request, url_for, flash, redirect
from flask_mail import Message
from smtplib import SMTPException
from werkzeug.datastructures import MultiDict
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm
from app.models import User


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid email!')
            return redirect(url_for('login'))
        if not user.check_password(form.password.data):
            flash('Invalid password!')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        flash('Successfully logged in!')
        return redirect(next_page)
    return render_template('login.html', title='Log In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Please, log out to register a new account!')
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have registered successfully! Please, log in!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Sign up', form=form)



@app.route('/logout')
def logout():
    logout_user()
    flash('Successfully logged out')
    return redirect(url_for('login'))


@app.route('/help')
def help_send():
    return render_template('help.html')


@app.route('/checker')
def checker():
    return render_template('form.html')


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
