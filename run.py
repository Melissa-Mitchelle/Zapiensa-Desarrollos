from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'

db = SQLAlchemy(app)


@app.before_first_request
def create_tables():
    db.create_all()

import views, models, resources

api.add_resource(resources.Curps, '/Curps')
api.add_resource(resources.Registros, '/Registros')
api.add_resource(resources.ReceiverData, '/Curps/<curp>')
api.add_resource(resources.CreateUser, '/createUser')
api.add_resource(resources.DeleteUser, '/deleteUser/<id_user>')
api.add_resource(resources.EditUser, '/editUser/<id_user>')
api.add_resource(resources.CreateReceiver, '/createReceiver')
api.add_resource(resources.DeleteReceiver, '/deleteReceiver')
api.add_resource(resources.EditReceiver, '/editReceiver/<receiver_curp>')
api.add_resource(resources.UserLogin, '/login')

if __name__ == '__main__':
     app.run(port='5002')
