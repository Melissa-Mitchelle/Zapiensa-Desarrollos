from flask_security.forms import RegisterForm, Required, LoginForm
from flask_wtf import FlaskForm
from marshmallow import fields, Schema
from datetime import datetime
from sqlalchemy.types import TIMESTAMP


from wtforms import StringField, SubmitField, validators

from config import db
from flask_security import UserMixin, RoleMixin

roles_users = db.Table('USERS_ROLES',
                       db.Column('id_user_role', db.Integer(), primary_key=True),
                       db.Column('id_user', db.Integer(), db.ForeignKey('USERS.id_user')),
                       db.Column('id_role', db.Integer(), db.ForeignKey('ROLES.id_role')))


class UserModel(db.Model, UserMixin):
    __tablename__ = 'USERS'

    id_user = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    s_name = db.Column(db.String(45), nullable=True)
    last_name = db.Column(db.String(45), nullable=False)
    s_last_name = db.Column(db.String(45), nullable=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(45), nullable=False)
    #    id_role = db.Column(db.Integer, db.ForeignKey("roles.id_role"), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_user = db.Column(db.Integer, nullable=False)
    created_time = db.Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    modified_user = db.Column(db.Integer, nullable=True)
    modified_time = db.Column(TIMESTAMP, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('USERS', lazy='dynamic'))

    def __init__(self, data):
        self.first_name = data.get('first_name')
        self.s_name = data.get('s_name')
        self.last_name = data.get('last_name')
        self.s_last_name = data.get('s_last_name')
        self.username = data.get('username')
        self.password = data.get('password')
        self.email = data.get('email')
        self.is_active = data.get('is_active')
        self.created_user = data.get('created_user')
        self.created_time = datetime.utcnow()
        self.modified_user = data.get('modified_user')
        self.modified_time = datetime.utcnow()

    def create(self):
        db.session.add(self)
        db.session.commit()


    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @staticmethod
    def get_all_users():
        return UserModel.query.all()

    @staticmethod
    def get_one_user(id_user):
        return UserModel.query.get(id_user)


class UserSchema(Schema):
    id_user = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    s_name = fields.Str(required=False)
    last_name = fields.Str(required=True)
    s_last_name = fields.Str(required=False)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Email(required=True)
    is_active = fields.Bool(required=True)
    created_user = fields.Integer(dump_only=True)
    created_time = fields.DateTime(dump_only=True)
    modified_user = fields.Integer(dump_only=True)
    modified_time = fields.DateTime(dump_only=True)


# Define the Role data-model
class Role(db.Model, RoleMixin):
    __tablename__ = 'ROLES'
    id_role = db.Column(db.Integer(), primary_key=True)
    role_name = db.Column(db.String(45), nullable=False)
    description = db.Column(db.String(256), nullable=False)


"""# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id_user_role = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id_user', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id_role', ondelete='CASCADE'))
"""


class ReceiverModel(db.Model):
    __tablename__ = 'RECEIVERS'

    id_receiver = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    s_name = db.Column(db.String(45), nullable=True)
    last_name = db.Column(db.String(45), nullable=False)
    s_last_name = db.Column(db.String(45), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    curp = db.Column(db.String(18), unique=True, nullable=False)
    p_phone = db.Column(db.String(18), nullable=False)
    s_phone = db.Column(db.String(18), nullable=True)
    address = db.Column(db.String(256), nullable=True)
    zip_code = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(45), nullable=True)
    created_user = db.Column(db.Integer, db.ForeignKey('USERS.id_user'), nullable=False)
    created_time = db.Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    modified_user = db.Column(db.Integer, db.ForeignKey('USERS.id_user'), nullable=True)
    modified_time = db.Column(TIMESTAMP, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)


    def __init__(self, data):
        self.first_name = data.get('first_name')
        self.s_name = data.get('s_name')
        self.last_name = data.get('last_name')
        self.s_last_name = data.get('s_last_name')
        self.age = data.get('age')
        self.curp = data.get('curp')
        self.p_phone = data.get('p_phone')
        self.s_phone = data.get('s_phone')
        self.address = data.get('address')
        self.zip_code = data.get('zip_code')
        self.email = data.get('email')
        self.created_user = data.get('created_user')
        self.created_time = datetime.utcnow()
        self.modified_user = data.get('modified_user')
        self.modified_time = datetime.utcnow()

    def create(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_curp(cls, curp):
        return cls.query.filter_by(curp=curp).first()

    @staticmethod
    def get_all_receivers():
        return ReceiverModel.query.all()

    @staticmethod
    def get_one_receiver(id_receiver):
        return ReceiverModel.query.get(id_receiver)


class ReceiverSchema(Schema):
    id_receiver = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    s_name = fields.Str(required=False)
    last_name = fields.Str(required=True)
    s_last_name = fields.Str(required=False)
    age = fields.Int(required=False)
    curp = fields.Str(required=True)
    p_phone = fields.Int(required=True)
    s_phone = fields.Int(required=False)
    address = fields.Str(required=False)
    zip_code = fields.Int(required=False)
    email = fields.Email(required=False)
    created_user = fields.Int(dump_only=True)
    created_time = fields.DateTime(dump_only=True)
    modified_user = db.Column(db.Integer, nullable=False)
    modified_time = fields.DateTime(dump_only=True)
