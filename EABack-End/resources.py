import datetime
import sqlalchemy
from flask import request, json, render_template, Response, make_response, redirect, url_for, session
from flask_restful import Resource, reqparse
from flask_security import Security, login_required, SQLAlchemyUserDatastore, roles_required, LoginForm
from flask_login import current_user, LoginManager
from flask_security.utils import hash_password
from marshmallow import utils
from config import app, db
from models import UserModel, UserSchema, ReceiverModel,\
    ReceiverSchema, ReceiverMirrorModel, ReceiverMirrorSchema, Roles


def clone_model(model):
    data = model
    attr = getattr(model, "id_user")
    setattr(data, "id", attr)

    return data


cUserModel = clone_model(UserModel)
print(cUserModel.__dict__)
user_schema = UserSchema()
receiver_schema = ReceiverSchema()
receiver_mirror_schema = ReceiverMirrorSchema()
user_datastore = SQLAlchemyUserDatastore(db, cUserModel, Roles)
security = Security(app, user_datastore)
#login_manager = LoginManager(app)
#principals = Principal(app)


"""@login_manager.user_loader
def load_user(userid):
    return user_datastore.find_user(id_user=userid)


@principals.identity_loader
def load_identity_from_weird_usecase():
    if current_user.is_active:
        identity = Identity(current_user.id_user)
        return identity
"""

class CheckRole(Resource):
    @login_required
    def get(self):
        ser_user = user_schema.dump(current_user)
        return ser_user['roles'][0]['role_name']


class Registros(Resource):
    @login_required
    def get(self):
        try:
            receivers = ReceiverModel.get_all_receivers()
            ser_receivers = receiver_schema.dump(receivers, many=True)
            return ser_receivers, 200
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class ReceiverData(Resource):
    def get(self, method, search_data):
        try:
            receiver = ReceiverModel.find(method, search_data)
            if receiver:
                ser_receiver = receiver_schema.dump(receiver, many=True)
                return ser_receiver, 200
            else:
                return {'message': 'User not found'}, 404
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class ReceiverDataGeneralSearch(Resource):
    def get(self, search_data):
        try:
            receiver = ReceiverModel.general_search(search_data)
            if receiver:
                ser_receiver = receiver_schema.dump(receiver, many=True)
                headers = {'Content-Type': 'text/html'}
                return {'message': ser_receiver}
            else:
                return 'User not found'
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class ReceiversByEvent(Resource):
    def get(self, event_id):
        try:
            receiver = ReceiverModel.get_by_event(event_id)
            if receiver:
                ser_receiver = receiver_schema.dump(receiver, many=True)
                headers = {'Content-Type': 'text/html'}
                return {'message': ser_receiver}
            else:
                return 'User not found'
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class ReceiverDataByCurpGuest(Resource):
    def get(self, curp):
        try:
            receiver = ReceiverModel.find_by_curp(curp)
            if receiver:
                ser_receiver = receiver_schema.dump(receiver, many=True)
                print(ser_receiver)
                return [{key: value for (key, value) in item.items() if
                        key in ['first_name', 'last_name', 'events', 'curp']} for item in ser_receiver], 200
            else:
                return make_response('User not found', 404)
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class ReceiverDataByCurp(Resource):
    @login_required
    def get(self, curp):
        try:
            receiver = ReceiverModel.find_by_curp(curp)
            if receiver:
                ser_receiver = receiver_schema.dump(receiver, many=True)
                return ser_receiver, 200
            else:
                return make_response('User not found', 404)
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class CreateUser(Resource):
    #    @roles_required('ADMINISTRADOR')
    def post(self):
        req_data = request.get_json()
        data = user_schema.load(req_data)

        try:
            if UserModel.find_by_username(data['username']):
                return {'message': 'User {} already exists'.format(data['username'])}
            user = UserModel(data)
            user.password = hash_password(user.password)
            user.create()
            return {
                'message': 'Usuario {} creado'.format(data['username'])
            }
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class DeleteUser(Resource):
    @roles_required('ADMINISTRADORISTRADOR')
    def delete(self, id_user):
        try:
            user = UserModel.get_one_user(id_user)
            ser_user = user_schema.dump(user)
            user.delete()
            return {
                       'message': 'Usuario {} borrado'.format(ser_user['username'])
                   }, 200
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class EditUser(Resource):
    @roles_required('ADMINISTRADORISTRADOR')
    def put(self, id_user):
        req_data = request.get_json()
        data = user_schema.load(req_data, partial=True)

        try:
            user = UserModel.get_one_user(id_user)
            user.update(data)
            ser_user = user_schema.dump(user)

            return {
                       'message': 'Usuario {} editado'.format(ser_user['username'])
                   }, 200
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class CreateReceiver(Resource):
    def post(self):
        req_data = request.get_json()
        data = receiver_schema.load(req_data)

        try:
            if ReceiverModel.find_by_curp(data['curp']):
                return {'message': 'Receiver {} already exists'.format(data['curp'])}
            receiver = ReceiverModel(data)
            receiver.create()
            return {
                'message': 'Beneficiario {} creado'.format(data['curp'])
            }
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class DeleteReceiver(Resource):
    @roles_required('ADMINISTRADORISTRADOR')
    def delete(self, id_receiver):
        try:
            receiver = ReceiverModel.get_one_receiver(id_receiver)
            ser_receiver = receiver_schema.dump(receiver)
            receiver.delete()
            return {
                       'message': 'Beneficiario {} borrado'.format(ser_receiver['curp'])
                   }, 200
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class EditReceiver(Resource):
    @roles_required('ADMINISTRADOR')
    def put(self, id_receiver):
        req_data = request.get_json()
        data = receiver_schema.load(req_data, partial=True)

        try:
            receiver = ReceiverModel.get_one_receiver(id_receiver)
            receiver.update(data)
            ser_receiver = receiver_schema.dump(receiver)

            return {
                       'message': 'Beneficiario {} editado'.format(ser_receiver['curp'])
                   }, 200
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class CreateReceiverMirror(Resource):
    #    @roles_required('VALIDADOR')
    def post(self):
        req_data = request.get_json()
        data = receiver_mirror_schema.load(req_data)
        try:
            receiver = ReceiverMirrorModel(data)
            receiver.create()
            ser_receiver = receiver_mirror_schema.dump(receiver)

            return {
                       'message': 'Beneficiario espejo {} creado'.format(ser_receiver['curp'])
                   }, 200
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class ReceiversModifications(Resource):
    @roles_required('ADMINISTRADOR')
    def get(self):
        both = []
        receivers_mirror = ReceiverMirrorModel.get_all()
        ser_receivers_mirror = receiver_mirror_schema.dump(receivers_mirror, many=True)
        for receiver_mirror in ser_receivers_mirror:
            both.append({'receiver': receiver_schema.
                        dump(ReceiverModel.get_one_receiver(receiver_mirror['id_receiver'])),
                         'mirror': receiver_mirror})
        return both


class ApproveReceiverModification(Resource):
    def get(self, id_receiver):

        receiver_mirror = ReceiverMirrorModel.get_one_receiver(id_receiver)
        ser_receiver_mirror = receiver_mirror_schema.dump(receiver_mirror)
        ser_receiver_id = ser_receiver_mirror['id_receiver']
        ser_receiver_mirror.pop('id_receiver_mirror')
        ser_receiver_mirror.pop('id_receiver')
        ser_receiver_mirror.pop('created_at')
        ser_receiver_mirror['modified_at'] = str(datetime.datetime.utcnow())
        data = receiver_schema.load(ser_receiver_mirror)
        try:
            receiver = ReceiverModel.get_one_receiver(ser_receiver_id)
            receiver.update(data)
            ReceiverMirrorModel.delete(receiver_mirror)
            ser_receiver = receiver_schema.dump(receiver)

            return {
                       'message': 'Beneficiario {} editado'.format(ser_receiver['curp'])
                   }, 200
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class Unauthorized(Resource):
    def get(self):
        return 'Unauthorized', 403
