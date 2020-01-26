import sqlalchemy
from flask import request, json, render_template, Response, make_response
from flask_restful import Resource, reqparse
from json import dumps
# from flask_jsonpify import jsonify
from flask_security import Security, login_required, SQLAlchemyUserDatastore, roles_required
from flask_security.utils import hash_password

from config import app, db

from models import UserModel, UserSchema, ReceiverModel, ReceiverSchema, Role

user_schema = UserSchema()
receiver_schema = ReceiverSchema()
user_datastore = SQLAlchemyUserDatastore(db, UserModel, Role)
security = Security(app, user_datastore)


class Curps(Resource):
    def get(self):
        # conn = db_connect.connect()  # connect to database
        query = db.execute("SELECT * FROM view_receivers")  # This line performs query and returns json result
        return {'curps': [i[2] for i in query.cursor.fetchall()]}  # Fetches first column that is CURP


class Registros(Resource):
    # @login_required
    def get(self):
        try:
            receivers = ReceiverModel.get_all_receivers()
            ser_receivers = receiver_schema.dump(receivers, many=True)
            return {
                       'message': ser_receivers
                   }, 200
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class ReceiverData(Resource):
    def get(self, curp):
        try:
            receiver = ReceiverModel.find_by_curp(curp)
            if receiver:
                ser_receiver = receiver_schema.dump(receiver)
                headers = {'Content-Type': 'text/html'}
                print(ser_receiver)
                return make_response(render_template('searchFormResult.html', first_name=ser_receiver["first_name"],
                                                     last_name=ser_receiver["last_name"], curp=ser_receiver["curp"]),
                                     200,
                                     headers)
            else:
                return 'User not found'
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500

        # return jsonify(result)


class CreateUser(Resource):
    @roles_required('admin')
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
    @roles_required('admin')
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
    @roles_required('admin')
    def put(self, id_user):
        req_data = request.get_json()
        data = user_schema.load(req_data, partial=True)

        try:
            user = UserModel.get_one_user(id_user)
            user.update(data)
            print(user_schema.dump(user))
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
                'message': 'Usuario {} creado'.format(data['curp'])
            }
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class DeleteReceiver(Resource):
    @roles_required('admin')
    def delete(self, id_receiver):
        try:
            receiver = ReceiverModel.get_one_receiver(id_receiver)
            ser_receiver = receiver_schema.dump(receiver)
            receiver.delete()
            return {
                       'message': 'Usuario {} borrado'.format(ser_receiver['curp'])
                   }, 200
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class EditReceiver(Resource):
    def put(self, id_receiver):
        req_data = request.get_json()
        data = receiver_schema.load(req_data, partial=True)

        try:
            receiver = ReceiverModel.get_one_receiver(id_receiver)
            receiver.update(data)
            print(receiver_schema.dump(receiver))
            ser_receiver = receiver_schema.dump(receiver)

            return {
                       'message': 'Usuario {} editado'.format(ser_receiver['curp'])
                   }, 200
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


def custom_response(res, status_code):
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )
