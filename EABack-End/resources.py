import sqlalchemy
from flask import request, render_template, make_response
from flask_restful import Resource
from flask_security import Security, login_required, SQLAlchemyUserDatastore, roles_required
from flask_login import current_user
from flask_security.utils import hash_password
from config import app, db
from models import UserModel, UserSchema, ReceiverModel, roles_users, \
    ReceiverSchema, ReceiverMirrorModel, ReceiverMirrorSchema, \
    Roles, ReceiverFollows, Events, ReceiversEvents, ReceiverEventsSchema, ReceiverFollowsSchema
import ex_db

def clone_model(model):
    data = model
    attr = getattr(model, "id_user")
    setattr(data, "id", attr)

    return data


cUserModel = clone_model(UserModel)
user_schema = UserSchema()
receiver_schema = ReceiverSchema()
receiver_mirror_schema = ReceiverMirrorSchema()
receiver_follows_schema = ReceiverFollowsSchema()
receiver_events_schema = ReceiverEventsSchema()
user_datastore = SQLAlchemyUserDatastore(db, cUserModel, Roles)
security = Security(app, user_datastore)


class CheckRole(Resource):
    @login_required
    def get(self):
        ser_user = user_schema.dump(current_user)
        return ser_user['roles'][0]['role_name']


class CreateFollow(Resource):
    @login_required
    def post(self):

        req_data = request.get_json()
        req_data.update({'id_user': current_user.id})
        errors = receiver_follows_schema.validate(req_data)
        if errors:
            return errors, 500
        data = receiver_follows_schema.load(req_data)
        try:
            if len(ReceiverFollows.query.filter_by(id_receiver_event=data['id_receiver_event']).all()) > 0:
                return {'message': 'El seguimiento {} ya existe'.format(data['id_receiver_event'])}
            follow = ReceiverFollows(data)
            follow.create()
            return {
                'message': 'Seguimiento creado'
            }
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class FollowUpdate(Resource):
    @login_required
    def put(self, id_follow):
        qryresult = ReceiverFollows.get_by_id(id_follow)
        if qryresult is not None:
            req_data = request.get_json()
            req_data['id_user'] = current_user.id
            req_data.pop('id_follow')
            errors = receiver_follows_schema.validate(req_data)
            if errors:
                return errors, 500
            data = receiver_follows_schema.load(req_data, partial=True)

            try:
                follow = ReceiverFollows.get_by_id(id_follow)
                follow.update(data)
                ser_follow = receiver_follows_schema.dump(follow)

                return {
                           'message': 'Seguimiento {} editado'.format(id_follow)
                       }, 200
            except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
                return render_template('500.html', error=e), 500
        else:
            return {'message': 'No se encontro este seguimiento.'}, 403

class Follows(Resource):
    @login_required
    def get(self):
        try:
            qryresult = db.session.query(ReceiversEvents, ReceiverModel, Events.name, Events.id_event, ReceiverFollows). \
                outerjoin(ReceiverModel, ReceiversEvents.id_receiver == ReceiverModel.id_receiver). \
                outerjoin(ReceiverFollows, ReceiverFollows.id_receiver_event == ReceiversEvents.id_receiver_event). \
                outerjoin(Events, ReceiversEvents.id_event == Events.id_event). \
                all()
            result = []
            i = 0
            for row in qryresult:
                result.append({**receiver_schema.dump(row.ReceiverModel),
                               **receiver_events_schema.dump(row.ReceiversEvents),
                               **receiver_follows_schema.dump(row.ReceiverFollows),
                               'event': row.name, 'id_event': row.id_event})
                i += 1
            return result, 200
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class ReceiverDataById(Resource):
    @login_required
    def get(self, id):
        try:
            receiver = ReceiverModel.get_one_receiver(id)
            if receiver:
                ser_receiver = receiver_schema.dump(receiver)
                return ser_receiver, 200
            else:
                return {'message': 'Not found'}, 404
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class ReceiverData(Resource):
    @login_required
    def get(self, method, search_data):
        try:
            receiver = ReceiverModel.find(method, search_data)
            if receiver:
                ser_receiver = receiver_schema.dump(receiver, many=True)
                return ser_receiver, 200
            else:
                return {'message': 'Not found'}, 404
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class ReceiversByEvent(Resource):
    @login_required
    def get(self, event_id):
        try:
            receiver = ReceiverModel.get_by_event(event_id)
            if receiver:
                ser_receiver = receiver_schema.dump(receiver, many=True)
                headers = {'Content-Type': 'text/html'}
                return {'message': ser_receiver}
            else:
                return 'Not found.'
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class ReceiverDataByCurpGuest(Resource):
    def get(self, curp):
        try:
            receiver = ReceiverModel.find_by_curp(curp)
            if receiver:
                ser_receiver = receiver_schema.dump(receiver, many=True)
                return [{key: value for (key, value) in item.items() if
                         key in ['first_name', 'last_name', 'events', 'curp']} for item in ser_receiver], 200
            else:
                return make_response('Not found', 404)
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class CreateUser(Resource):
    @roles_required('ADMINISTRADOR')
    def post(self):
        req_data = request.get_json()
        req_data['created_user'] = current_user.id
        role = req_data['roles']
        req_data.pop('roles')
        errors = user_schema.validate(req_data)
        if errors:
            return errors, 500
        data = user_schema.load(req_data)
        try:
            if UserModel.find_by_username(data['username']):
                return {'message': 'User {} already exists'.format(data['username'])}
            user = UserModel(data)
            user.password = hash_password(user.password)
            user.create()
            ins = roles_users.insert().values(id_user=user.id_user, id_role=role)
            ins.compile().params
            result = db.session.execute(ins)
            db.session.commit()
            return {
                'message': 'Usuario {} creado'.format(data['username'])
            }
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class DeleteUser(Resource):
    @roles_required('ADMINISTRADOR')
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
        errors = user_schema.validate(req_data)
        if errors:
            return errors, 500
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
    @roles_required('ADMINISTRADORISTRADOR')
    def post(self):
        req_data = request.get_json()
        req_data.update({'created_user': current_user.id})
        errors = receiver_schema.validate(req_data)
        if errors:
            return errors, 500
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
        errors = receiver_schema.validate(req_data)
        if errors:
            return errors, 500
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
    @roles_required('VALIDADOR')
    def post(self):
        req_data = request.get_json()
        req_data.update({'modified_user': current_user.id})
        errors = receiver_mirror_schema.validate(req_data)
        if errors:
            return errors, 500
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


class CancelReceiverModification(Resource):
    @roles_required('ADMINISTRADOR')
    def get(self, id_receiver):
        receiver_mirror = ReceiverMirrorModel.get_one_receiver(id_receiver)
        try:
            ReceiverMirrorModel.delete(receiver_mirror)
            return {
                       'message': 'Beneficiario espejo {} creado'.format(id_receiver)
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
    @roles_required('ADMINISTRADORISTRADOR')
    def get(self, id_receiver):

        receiver_mirror = ReceiverMirrorModel.get_one_receiver(id_receiver)
        ser_receiver_mirror = receiver_mirror_schema.dump(receiver_mirror)
        ser_receiver_id = ser_receiver_mirror['id_receiver']
        ser_receiver_mirror.pop('id_receiver_mirror')
        ser_receiver_mirror.pop('id_receiver')
        ser_receiver_mirror.pop('modified_time')
        #        ser_receiver_mirror.pop('created_time')
        #        ser_receiver_mirror['modified_time'] = str(datetime.datetime.utcnow())
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

"""
class ImportFromSheet(Resource):
    #    @roles_required('ADMINISTRADOR')
    def get(self, filename):
        try:
            dirname = os.path.dirname(__file__)
            filename_path = os.path.join(dirname, '../shared/' + filename)
            return jsonify({"result": filename_path.absolute()})
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500
"""

class Unauthorized(Resource):
    def get(self):
        return 'Unauthorized', 403
