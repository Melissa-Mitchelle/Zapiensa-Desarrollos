from sqlalchemy import ForeignKey
from run import db
from marshmallow import fields, Schema
import datetime


class UserModel(db.Model):
    __tablename__ = 'USERS'

    id_user = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    username = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(45), nullable=False)
#    id_role = db.Column(db.Integer, ForeignKey("roles.id_role"), nullable=False)
    id_role = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.username = data.get('username')
        self.password = data.get('password')
        self.email = data.get('email')
        self.id_role = data.get('id_role')
        self.is_active = data.get('is_active')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

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
        return cls.query.filter_by(username = username).first()

    @staticmethod
    def get_all_users():
        return UserModel.query.all()

    @staticmethod
    def get_one_user(id_user):
        return UserModel.query.get(id_user)


class UserSchema(Schema):
    id_user = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Email(required=True)
    id_role = fields.Int(required=True)
    is_active = fields.Bool(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)


class ReceiverModel(db.Model):
    __tablename__ = 'RECEIVERS'

    id_receiver = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    curp = db.Column(db.String(18), nullable=False)
    p_phone = db.Column(db.String(18), nullable=False)
    s_phone = db.Column(db.String(18), nullable=True)
    address = db.Column(db.String(250), nullable=False)
    zip_code = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(45), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
    modified_user = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.age = data.get('age')
        self.curp = data.get('curp')
        self.p_phone = data.get('p_phone')
        self.s_phone = data.get('s_phone')
        self.address = data.get('address')
        self.zip_code = data.get('zip_code')
        self.email = data.get('email')
        self.is_active = data.get('is_active')
        self.modified_user = data.get('modified_user')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

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
    def get_all_users():
        return UserModel.query.all()

    @staticmethod
    def get_one_receiver(id_receiver):
        return UserModel.query.get(id_receiver)


class ReceiverSchema(Schema):
    id_receiver = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    age = fields.Int(required=True)
    curp = fields.Str(required=True)
    p_phone = fields.Int(required=True)
    s_phone = fields.Int(required=False)
    address = fields.Str(required=True)
    zip_code = fields.Int(required=False)
    email = fields.Email(required=True)
    is_active = fields.Bool(required=True)
    modified_user = db.Column(db.Integer, nullable=False)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
