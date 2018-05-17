from sqlalchemy import desc
from flask import (
    render_template, request, url_for, flash,
    redirect, jsonify, make_response, escape
)
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.models import User, Message, MessageField
from app.email import send_email


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template(
        'index.html',
        messages=current_user.messages.order_by(desc(Message.date)),
        checkbox_status=current_user.email_notifications_status()
    )


@bp.route('/delete_message/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    MessageField.query.filter_by(message_id=message_id).delete()
    Message.query.filter_by(id=message_id).delete()
    db.session.commit()
    flash('Your message was removed successfully!', 'success')
    return redirect(url_for('main.index'))


@bp.route('/help')
def help_send():
    return render_template('help.html', title='Help')


@bp.route('/what_is_it')
def what_is_it():
    return render_template('help.html', title='What is it?', what=True)


@bp.route('/checker')
def checker():
    return render_template('form.html')


@bp.route('/all_users')
def all_users():
    return render_template('all_users.html', users=User.query.all(), title='All users')


@bp.route('/send', methods=['POST'])
def flask_send():
    data = request.form
    token = request.args.get('token')
    user = User.query.filter_by(token=token).first()
    if user is None:
        resp = make_response(jsonify({'status': 'Not found user'}), 404)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    # current message
    message = Message(user_id=user.id)
    db.session.add(message)
    db.session.commit()

    # fill message fields
    for m_name, m_data in data.items():
        field = MessageField(
            field_name=escape(str(m_name)),
            field_data=escape(str(m_data)),
            message_id=message.id
        )
        db.session.add(field)
    db.session.commit()

    # send on email
    if user.email_notifications:
        send_email(user, message)

    resp = make_response(jsonify({'status': 'Created new message'}), 201)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@bp.route('/set_mail_checkbox', methods=['POST'])
@login_required
def set_mail_checkbox():
    try:
        status = request.form['setter']
    except:
        status = 'off'
    print(status)
    current_user.email_notifications = True if status == 'on' else False
    db.session.commit()
    flash('Email notifications ' + status, 'success')
    return redirect(url_for('main.index'))
