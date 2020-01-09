import sqlalchemy
from flask import request, json, render_template, Response
from flask_restful import Resource, reqparse
from json import dumps
from flask_jsonpify import jsonify
from models import UserModel, UserSchema, ReceiverModel, ReceiverSchema

user_schema = UserSchema()
receiver_schema = ReceiverSchema()


class Curps(Resource):
    def get(self):
        conn = db_connect.connect() # connect to database
        query = conn.execute("select * from Benfs") # This line performs query and returns json result
        return {'curps': [i[0] for i in query.cursor.fetchall()]} # Fetches first column that is CURP


class Registros(Resource):
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
            receiver = UserModel.get_one_receiver(curp)
            ser_receiver = receiver_schema.dump(receiver)
            return {
                       'message': ser_receiver
                   }, 200
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500

        #return jsonify(result)


class CreateUser(Resource):
    def post(self):
        req_data = request.get_json()
        data = user_schema.load(req_data)

        try:
            if UserModel.find_by_username(data['username']):
                return {'message': 'User {} already exists'.format(data['username'])}
            user = UserModel(data)
            user.create()
            return {
                'message': 'Usuario {} creado'.format(data['username'])
            }
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            return render_template('500.html', error=e), 500


class DeleteUser(Resource):
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


class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help='This field cannot be blank', required=True)
        parser.add_argument('password', help='This field cannot be blank', required=True)
        data = parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])
        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}

        if data['password'] == current_user.password:
            return {'message': 'Logged in as {}'.format(current_user.username)}
        else:
            return {'message': 'Wrong credentials'}


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