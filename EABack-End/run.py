from config import api, db, app
import views
import models
import resources
from flask import session


@app.before_first_request
def create_tables():
    db.create_all()


api.add_resource(resources.Follows, '/follows')
#api.add_resource(resources.ReceiverDataByCurp, '/Curps/<curp>')
api.add_resource(resources.ReceiverDataById, '/receiver/<id>')
api.add_resource(resources.ReceiverDataByCurpGuest, '/CurpsGuest/<curp>')
api.add_resource(resources.ReceiverData, '/searchReceiver/<method>/<search_data>')
api.add_resource(resources.ReceiversByEvent, '/receiversByEvent/<event_id>')
api.add_resource(resources.CreateUser, '/createUser')
api.add_resource(resources.DeleteUser, '/deleteUser/<id_user>')
api.add_resource(resources.EditUser, '/editUser/<id_user>')
api.add_resource(resources.CreateReceiver, '/createReceiver')
api.add_resource(resources.DeleteReceiver, '/deleteReceiver')
api.add_resource(resources.EditReceiver, '/editReceiver/<id_receiver>')
api.add_resource(resources.CreateReceiverMirror, '/createReceiverMirror')
api.add_resource(resources.ApproveReceiverModification, '/approveReceiverModification/<id_receiver>')
api.add_resource(resources.CancelReceiverModification, '/cancelReceiverModification/<id_receiver>')
api.add_resource(resources.FollowUpdate, '/followUpdate/<id_follow>')
api.add_resource(resources.CreateFollow, '/createFollow')
api.add_resource(resources.ReceiversModifications, '/receiversModifications')
api.add_resource(resources.Unauthorized, '/unauthorized')
api.add_resource(resources.CheckRole, '/checkrole')
api.add_resource(resources.CheckEvents, '/checkEvents')
api.add_resource(resources.Statistics, '/statistics')
#api.add_resource(resources.ImportFromSheet, '/importFromSheet')

if __name__ == '__main__':
    app.run(port='5002')
