from config import api, db, app
import views
import models
import resources


@app.before_first_request
def create_tables():
    db.create_all()


api.add_resource(resources.Curps, '/Curps')
api.add_resource(resources.Registros, '/Registros')
api.add_resource(resources.ReceiverData, '/Curps/<curp>')
api.add_resource(resources.CreateUser, '/createUser')
api.add_resource(resources.DeleteUser, '/deleteUser/<id_user>')
api.add_resource(resources.EditUser, '/editUser/<id_user>')
api.add_resource(resources.CreateReceiver, '/createReceiver')
api.add_resource(resources.DeleteReceiver, '/deleteReceiver')
api.add_resource(resources.EditReceiver, '/editReceiver/<receiver_curp>')

if __name__ == '__main__':
    app.run(port='5002')
