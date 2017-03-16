# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from . import auth
from .forms import LoginForm, JxnuLoginForm, RegistrationForm,successful_form
from .models import UserProfile
from .. import db
from ..email import send_email
from is_jxnuer import is_jxnuer


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    Jform = JxnuLoginForm()
    if form.submit1.data and form.validate_on_submit():
        user = UserProfile.query.filter_by(account=form.account.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'邮箱或密码错误')
    if Jform.submit2.data and Jform.validate_on_submit():
        if Jform.role.data == 1:
            user = UserProfile.query.filter_by(account=Jform.student_id.data).first()
            if user is not None and user.verify_password(Jform.password.data):
                login_user(user,remember=True)
                return redirect(request.args.get('next') or url_for('main.index'))
            who = is_jxnuer(Jform.student_id.data,Jform.password.data,'Student')
            if who.get_cookies() and   who.get_name():
                user = UserProfile(account=Jform.student_id.data,password=Jform.password.data,username=who.get_name())
                db.session.add(user)
                db.session.commit()
            flash(u'学号或密码错误。')
        if Jform.role.data == 0:
            teacher = UserProfile.query.filter_by(account=Jform.student_id.data).first()
            if teacher is not None and teacher.verify_password(Jform.password.data):
                login_user(teacher,remember=True)
                return redirect(request.args.get('next') or url_for('main.index'))
            who = is_jxnuer(Jform.student_id.data,Jform.password.data,'Teacher')
            if who.get_cookies() and who.get_name():
                teacher = UserProfile(account=Jform.student_id.data,password=Jform.password.data,username=who.get_name(),
                                      auth_info=0)
                db.session.add(teacher)
                db.session.commit()
            flash(u'教号或密码错误。')

    return render_template('auth/login.html', form=form , Jform=Jform)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.submit1.data and successful_form(form):
        user = UserProfile(account=form.account.data, username=form.username.data,
                           password=form.password.data,sex=form.sex.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        token = user.generate_confirmation_token()
        send_email(user.account,u'验证你的账户','auth/email/confirm',user=user,token=token)
        flash(u'验证邮箱已经发送至你的邮箱，请注意查收')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if hasattr(current_user, confirm):
        if current_user.confirm(token):
            flash(u'验证成功')
        else:
            flash(u'验证失败，链接可能失效')
    return redirect(url_for('main.index'))

@auth.route('/teacher_confirm')
@login_required
def teacher_confirm():
    return render_template('auth/techer_confirm.html',user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已经注销了')
    return redirect(url_for('main.index'))


