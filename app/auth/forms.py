# -*- coding: utf-8 -*-
from flask import flash
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, RadioField
from wtforms.validators import InputRequired, Length, Email, Regexp, EqualTo

from .models import UserProfile


class LoginForm(Form):
    account = StringField('Email', validators=[InputRequired(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[InputRequired()])
    remember_me = BooleanField(u'记住我')
    submit1 = SubmitField(u'登录')


class JxnuLoginForm(Form):
    role = RadioField(coerce=int, choices=[(1, u'学生'), (0, u'教工')], default=1)
    student_id = StringField(u'学号', validators=[InputRequired(), Length(1, 100)])
    password = PasswordField(u'密码', validators=[InputRequired(), Length(1, 30)])
    submit2 = SubmitField(u'登录')


class RegistrationForm(Form):
    account = StringField('Email', validators=[InputRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[InputRequired(), Length(1, 64),
                           Regexp('^[a-zA-Z0-9_u4e00-u9fa5]+$', message=u'只能包含中英文下划线')])
    school = StringField(u'学习单位', validators=[Length(0,64)])
    sex = RadioField(coerce=int,choices=[(1,u'男'),(0,u'女')],default=1)
    password = PasswordField(u'密码', validators=[InputRequired(), Length(1, 30), EqualTo('password2', message=u'上下密码不一致')])
    password2 = PasswordField(u'确认密码', validators=[InputRequired()])
    submit1 = SubmitField(u'注册')

    def has_account(self):
        if UserProfile.query.filter_by(account=self.account.data).first():
            return True

    def has_username(self):
        if UserProfile.query.filter_by(username=self.username.data).first():
            return True

    def __repr__(self):
        return 'UserForm'



def successful_form(form):
    if form.validate_on_submit():
        if form.has_account():
            flash(u'邮箱已经注册了。',category=str(form))
            return False
        elif form.has_username():
            flash(u'用户名已经被注册了。',category=str(form))
            return False
        else:
            return True
    return False

