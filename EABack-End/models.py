from marshmallow import fields, Schema
from datetime import datetime
from sqlalchemy import or_
from marshmallow_sqlalchemy import ModelSchema
from config import db
from flask_security import UserMixin, RoleMixin
from sqlalchemy.ext.associationproxy import association_proxy

fields.Field.default_error_messages["required"] = "Este campo es requerido."
fields.Field.default_error_messages["null"] = "Por favor completa este campo."
fields.Field.default_error_messages["validator_failed"] = "Valor invalido."

roles_users = db.Table('USERS_ROLES',
                       db.Column('id_user_role', db.Integer(), primary_key=True),
                       db.Column('id_user', db.Integer(), db.ForeignKey('USERS.id_user')),
                       db.Column('id_role', db.Integer(), db.ForeignKey('ROLES.id_role')))


class UserModel(db.Model, UserMixin):
    __tablename__ = 'USERS'

    id_user = db.Column(db.Integer, primary_key=True)
    given_name = db.Column(db.String(90), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    s_last_name = db.Column(db.String(45), nullable=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(45), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_user = db.Column(db.Integer, nullable=False)
    created_time = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    modified_user = db.Column(db.Integer, nullable=True)
    modified_time = db.Column(db.TIMESTAMP, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    roles = db.relationship('Roles', secondary=roles_users,
                            backref=db.backref('USERS', lazy='dynamic'))

    def __init__(self, data):
        self.given_name = data.get('given_name')
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

    def has_role(self, role):
        return role in self.roles


# Define the Role data-model
class Roles(db.Model, RoleMixin):
    __tablename__ = 'ROLES'
    id_role = db.Column(db.Integer(), primary_key=True)
    role_name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(256), nullable=False)

    @property
    def id(self):
        return self.id_role

    @property
    def name(self):
        return self.role_name

    @name.setter
    def name(self, _name):
        self.role_name = _name


class RoleSchema(Schema):
    id_role = fields.Int(dump_only=True)
    role_name = fields.Str(required=True)
    name = role_name
    description = fields.Str(required=True)
    id = id_role


class UserSchema(Schema):
    id_user = fields.Int(dump_only=True)
    given_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    s_last_name = fields.Str(required=False)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Email(required=True)
    is_active = fields.Bool(required=False, default=True)
    created_user = fields.Integer(required=True)
    created_time = fields.DateTime(dump_only=True)
    modified_user = fields.Integer(dump_only=True)
    modified_time = fields.DateTime(dump_only=True)
    roles = fields.Nested(RoleSchema, many=True, only=("role_name",))



class Events(db.Model):
    __tablename__ = 'EVENTS'
    id_event = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    def __init__(self, data):
        self.name = data.get('name')

    @staticmethod
    def get_all():
        return Events.query.all()

    def create(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_one(id_event):
        return Events.query.get(id_event)


class EventsSchema(Schema):
    id_event = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class ReceiverModel(db.Model):
    __tablename__ = 'RECEIVERS'

    id_receiver = db.Column(db.Integer, primary_key=True)
    given_name = db.Column(db.String(90), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    s_last_name = db.Column(db.String(45), nullable=True)
    curp = db.Column(db.String(18), unique=True, nullable=False)
    birthdate = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(1), nullable=True)
    p_phone = db.Column(db.String(18), nullable=False)
    s_phone = db.Column(db.String(18), nullable=True)
    address = db.Column(db.String(256), nullable=True)
    zip_code = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(45), nullable=True)
    created_user = db.Column(db.Integer, db.ForeignKey('USERS.id_user'), nullable=False)
    created_time = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    modified_user = db.Column(db.Integer, db.ForeignKey('USERS.id_user'), nullable=True)
    modified_time = db.Column(db.TIMESTAMP, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    events = association_proxy('receivers_events', 'event', creator=lambda event: ReceiversEvents(event=event))

    def __init__(self, data):
        self.given_name = data.get('given_name')
        self.last_name = data.get('last_name')
        self.s_last_name = data.get('s_last_name')
        self.curp = data.get('curp')
        self.birthdate = data.get('birthdate')
        self.gender = data.get('gender')
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

    @staticmethod
    def find_by_curp(curp):
        return ReceiverModel.query.filter_by(curp=curp).all()

    @staticmethod
    def get_by_event(event_id):
        return ReceiverModel.query.join(ReceiversEvents).filter(ReceiversEvents.id_event == event_id).all()

    @staticmethod
    def get_all_receivers():
        return ReceiverModel.query.all()

    @staticmethod
    def get_one_receiver(id_receiver):
        return ReceiverModel.query.get(id_receiver)

    @staticmethod
    def find(method, search_data):
        if method == "curp":
            return ReceiverModel.query.filter(ReceiverModel.curp.contains(search_data)).all()
        elif method == "name":
            print(search_data)
            return ReceiverModel.query.filter(
                (ReceiverModel.given_name + ' ' + ReceiverModel.last_name
                 + ' ' + ReceiverModel.s_last_name
                 ).contains(search_data)
            ).all()
        elif method == "phone":
            return ReceiverModel.query.filter(or_(ReceiverModel.p_phone.contains(search_data),
                                                  ReceiverModel.s_phone.contains(search_data))).all()
        elif method == "general":
            return ReceiverModel.query.filter(or_(ReceiverModel.p_phone.contains(search_data),
                                                  ReceiverModel.s_phone.contains(search_data),
                                                  ReceiverModel.curp.contains(search_data),
                                                  ReceiverModel.address.contains(search_data),
                                                  ReceiverModel.zip_code.contains(search_data),
                                                  ReceiverModel.email.contains(search_data),
                                                  (
                                                          ReceiverModel.given_name + ' ' + ReceiverModel.last_name
                                                          + ' ' + ReceiverModel.s_last_name
                                                  ).contains(search_data)
                                                  )).all()


class ReceiverFollows(db.Model):
    __tablename__ = 'FOLLOWS'
    id_follow = db.Column(db.Integer(), primary_key=True)
    id_receiver_event = db.Column(db.Integer, db.ForeignKey("EVENTS.id_event"), nullable=False)
    notification_no = db.Column(db.Integer, nullable=True)
    notificated = db.Column(db.Boolean, nullable=True)
    attendance = db.Column(db.Boolean, nullable=True)
    id_user = db.Column(db.Integer, db.ForeignKey("USERS.id_user"), nullable=False)
    modified_time = db.Column(db.DateTime)
#    receiver = db.relationship('ReceiverModel')

    def __init__(self, data):
        self.id_receiver_event = data.get('id_receiver_event')
        self.notification_no = data.get('notification_no')
        self.notificated = data.get('notified')
        self.attendance = data.get('attendance')
        self.id_user = data.get('id_user')
        self.modified_time = datetime.utcnow()
        self.receiver = data.get('receiver')

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

    @staticmethod
    def get_all():
        return ReceiverFollows.query.all()

    @staticmethod
    def get_by_id(id_follow):
        return ReceiverFollows.query.get(id_follow)


class ReceiverFollowsSchema(Schema):
    id_follow = fields.Int(dump_only=True)
    id_receiver_event = fields.Int(required=False)
    id_user = fields.Int(required=True)
    notification_no = fields.Int(required=False)
    notificated = fields.Bool(required=False)
    attendance = fields.Bool(required=False)
    modified_time = fields.DateTime(dump_only=True)
#    receiver = fields.Nested(ReceiverModel, many=True)
    



class ReceiversEvents(db.Model):
    __tablename__ = 'RECEIVERS_EVENTS'
    id_receiver_event = db.Column(db.Integer(), primary_key=True, nullable=False)
    id_receiver = db.Column(db.Integer(), db.ForeignKey("RECEIVERS.id_receiver"), nullable=False)
    id_event = db.Column(db.Integer(), db.ForeignKey("EVENTS.id_event"), nullable=False)
    receiver = db.relationship('ReceiverModel', backref=db.backref('receivers_events', cascade='all, delete-orphan'))
    event = db.relationship('Events')


class ReceiverEventsSchema(ModelSchema):
    class Meta:
        model = ReceiversEvents


class ReceiverSchema(Schema):
    id_receiver = fields.Int(dump_only=True)
    given_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    s_last_name = fields.Str(required=False)
    curp = fields.Str(required=True)
    birthdate = fields.Date(required=False, allow_none=True)
    gender = fields.Str(required=False)
    p_phone = fields.Int(required=True)
    s_phone = fields.Int(required=False, allow_none=True)
    address = fields.Str(required=False)
    events = fields.Nested(EventsSchema, many=True)
    zip_code = fields.Int(required=False,  allow_none=True)
    email = fields.Email(required=False, allow_none=True)
    created_user = fields.Int(required=False)
    created_time = fields.DateTime(dump_only=True)
    modified_user = fields.Int(required=False)
    modified_time = fields.DateTime(dump_only=True)


class ReceiverMirrorModel(db.Model):
    __tablename__ = 'RECEIVERS_MIRROR'

    id_receiver_mirror = db.Column(db.Integer, primary_key=True)
    id_receiver = db.Column(db.Integer, db.ForeignKey("RECEIVERS.id_receiver"), nullable=False)
    given_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    s_last_name = db.Column(db.String(45), nullable=False)
    curp = db.Column(db.String(18), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    p_phone = db.Column(db.String(18), nullable=False)
    s_phone = db.Column(db.String(18), nullable=True)
    address = db.Column(db.String(250), nullable=False)
    zip_code = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(45), nullable=True)
    modified_user = db.Column(db.Integer, db.ForeignKey("USERS.id_user"), nullable=False)
    modified_time = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, data):
        self.id_receiver = data.get('id_receiver')
        self.given_name = data.get('given_name')
        self.last_name = data.get('last_name')
        self.s_last_name = data.get('s_last_name')
        # self.curp = data.get('curp')
        self.birthdate = data.get('birthdate')
        self.gender = data.get('gender')
        self.p_phone = data.get('p_phone')
        self.s_phone = data.get('s_phone')
        self.address = data.get('address')
        self.zip_code = data.get('zip_code')
        self.email = data.get('email')
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

    @staticmethod
    def get_one_receiver(id_receiver):
        return ReceiverMirrorModel.query.get(id_receiver)

    @staticmethod
    def get_all():
        return ReceiverMirrorModel.query.all()


class ReceiverMirrorSchema(Schema):
    id_receiver_mirror = fields.Int(dump_only=True)
    id_receiver = fields.Int(required=True)
    given_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    s_last_name = fields.Str(required=True)
    curp = fields.Str(required=True)
    birthdate = fields.Date(required=False)
    gender = fields.Str(required=False)
    p_phone = fields.Int(required=True)
    s_phone = fields.Str(required=False, allow_none=True)
    address = fields.Str(required=False)
    zip_code = fields.Int(required=False, allow_none=True)
    email = fields.Email(required=False, allow_none=True)
    modified_user = fields.Int(required=True)
    modified_time = fields.DateTime(dump_only=True)
