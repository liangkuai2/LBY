# -*- coding: utf-8 -*-
from .. import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return UserProfile.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('UserProfile', backref='role')
    teacher = db.relationship('Teacher', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


class UserProfile(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, index=True)
    account = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    sex = db.Column(db.Integer, default=1)  # 1表示性别男，0表示性别女
    school = db.Column(db.String(64))  # 学习单位
    description = db.Column(db.String(128), default=u'')
    image = db.Column(db.String(72), default='image/default.png')
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    auth_id = db.Column(db.Integer, db.ForeignKey('user_auth.id'))
    add_time = db.Column(db.String(64), default=datetime.now)

    @property
    def password(self):
        raise AttributeError('password is not a readle attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def __repr__(self):
        return '<User %r>' % self.username


class Teacher(db.Model, UserMixin):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    account = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    work_location = db.Column(db.String(128))  # 工作单位
    work_position = db.Column(db.String(64))  # 工作职位
    points = db.Column(db.String(128))  # 个人简述
    image = db.Column(db.String(72), default='image/default.png')
    sex = db.Column(db.Integer, default=1)  # 1表示性别男，0表示性别女
    confirmed = db.Column(db.Boolean, default=False)
    click_nums = db.Column(db.Integer, default=0)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    auth_id = db.Column(db.Integer, db.ForeignKey('user_auth.id'))
    add_time = db.Column(db.String(64), default=datetime.now)

    @property
    def password(self):
        raise AttributeError('password is not a readle attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


class UserAuth(db.Model):
    __tablename__ = 'user_auth'
    id = db.Column(db.Integer, primary_key=True)
    auth_name = db.Column(db.String(64), unique=True)
    users = db.relationship('UserProfile', backref='auth')
    teachers = db.relationship('Teacher', backref='auth')
