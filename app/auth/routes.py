from flask import render_template, request, url_for, flash, redirect
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user

from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid email!', 'danger')
            return redirect(url_for('auth.login'))
        if not user.check_password(form.password.data):
            flash('Invalid password!', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        flash('Successfully logged in!', 'success')
        return redirect(next_page)
    return render_template('auth/login.html', title='Log In', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Please, log out to register a new account!', 'info')
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        user.set_token()
        db.session.commit()
        flash('You have registered successfully! Please, log in!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Sign up', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    flash('Successfully logged out', 'success')
    return redirect(url_for('auth.login'))
