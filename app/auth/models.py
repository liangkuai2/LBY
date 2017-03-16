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


class Permission:
    """
    """
    COMMENT_FOLLOW_COLLECT = 0x01
    UPLOAD_RESOURCE = 0x02
    UPLOAD_VIDEO = 0x04
    WRITE_ARTICLE = 0x08
    DELETE_VIDEO = 0x10
    DELETE_RESOURCE = 0x20
    DELETE_ARTICLE = 0x40
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('UserProfile', backref='role')

    @staticmethod
    def insert_roles():
        roles = {
            'Student': (Permission.COMMENT_FOLLOW_COLLECT |
                        Permission.UPLOAD_RESOURCE |
                        Permission.WRITE_ARTICLE, True),
            'Teacher': (Permission.COMMENT_FOLLOW_COLLECT |
                        Permission.UPLOAD_RESOURCE |
                        Permission.UPLOAD_VIDEO |
                        Permission.WRITE_ARTICLE, False),
            'SchoolAdmin': (Permission.COMMENT_FOLLOW_COLLECT |
                            Permission.UPLOAD_VIDEO |
                            Permission.UPLOAD_RESOURCE |
                            Permission.WRITE_ARTICLE |
                            Permission.DELETE_ARTICLE |
                            Permission.DELETE_RESOURCE |
                            Permission.DELETE_VIDEO, False),
            'Admin': (0xff, False)

        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


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
    description = db.Column(db.String(128), default=u'') # 个人简述
    image = db.Column(db.String(72), default='image/default.png')
    interested_field = db.Column(db.Integer)  # 二进制表示 0b1表示计算机学科 0b10表示教育学科
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    auth_id = db.Column(db.Integer, db.ForeignKey('user_auth.id'))
    auth_info = db.Column(db.Integer, default=1) # 认证方式信息 1表示jxnu学生或者邮箱登录的用户 0表示以jxnu老师登录的用户
    add_time = db.Column(db.String(64), default=datetime.utcnow)

    def __init__(self,**kwargs):
        super(UserProfile, self).__init__(**kwargs)
        if self.role is None:
            if self.account == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None and self.account in current_app.config['SCHOOLADMIN']:
                self.role = Role.query.filter_by(name='SchoolAdmin').first()
            if self.role is None and self.auth == 'jxnu_id' and self.auth_info == 0:
                self.role = Role.query.filter_by(name='Teacher').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()



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


class UserAuth(db.Model):
    __tablename__ = 'user_auth'
    id = db.Column(db.Integer, primary_key=True)
    auth_name = db.Column(db.String(64), unique=True)
    users = db.relationship('UserProfile', backref='auth')

    @staticmethod
    def insert_auth():
        auth_names = ['email','jxnu_id']
        for a in auth_names:
            user_auth = UserAuth.query.filter_by(auth_name=a).first()
            if user_auth is None:
                user_auth = UserAuth(auth_name=a)
                db.session.add(user_auth)
        db.session.commit()
