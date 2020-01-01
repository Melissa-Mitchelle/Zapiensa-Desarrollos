from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify

parser = reqparse.RequestParser()
db_connect = create_engine('sqlite:///PBdata.db')
app = Flask(__name__)
api = Api(app)

class Curps(Resource):
    def get(self):
        conn = db_connect.connect() # connect to database
        query = conn.execute("select * from Benfs") # This line performs query and returns json result
        return {'curps': [i[0] for i in query.cursor.fetchall()]} # Fetches first column that is CURP

class Registros(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select be_curp, be_name, be_telh, be_telm from Benfs;")
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)

class BenfsData(Resource):
    def get(self, be_curp):
        conn = db_connect.connect()
        query = conn.execute("select * from Benfs where be_curp = '{}'".format(be_curp))
        result = {'data': [dict(zip(tuple(query.keys()), i)) for i in query.cursor]}
        return jsonify(result)

class Create_new_register(Resource):
    def post(self):
        conn = db_connect.connect()
        parser.add_argument('be_curp', type=str)
        parser.add_argument('be_name', type=str)
        parser.add_argument('be_telh', type=str)
        parser.add_argument('be_telm', type=str)
        parser.add_argument('be_codp', type=str)
        parser.add_argument('be_email', type=str)
        parser.add_argument('be_asis', type=int)
        parser.add_argument('be_conf', type=int)
        args = parser.parse_args()
        values = list(args.values())
        query = conn.execute("""insert into Benfs values('{}','{}','{}','{}','{}','{}',{},{})""".format(values[0],values[1],values[2],
                                                                                          values[3],values[4],values[5],
                                                                                          values[6],values[7]))

        ##return {'query': str(query)}

class Delete_Register(Resource):
    def delete(self):
        conn = db_connect.connect()
        parser.add_argument('be_curp', type=str)
        args = parser.parse_args()
        values = list(args.values())
        query = """DELETE FROM Benfs WHERE be_curp == values('{}')""".format(values[0])
        return {'query' : str(query)}

class Edit_Register(Resource):
    def put(self, be_curp):
        conn = db_connect.connect()
        parser.add_argument('be_curp', type=str)
        parser.add_argument('be_name', type=str)
        parser.add_argument('be_telh', type=str)
        parser.add_argument('be_telm', type=str)
        parser.add_argument('be_codp', type=str)
        parser.add_argument('be_email', type=str)
        parser.add_argument('be_asis', type=int)
        parser.add_argument('be_conf', type=int)
        args = parser.parse_args()
        values = list(args.values())
        query = conn.execute("""UPDATE Benfs 
                    SET be_name = '{}',
                        be_telh = '{}',
                        be_telm = '{}',
                        be_codp = '{}',
                        be_email = '{}',
                        be_asis = '{}',
                        be_conf = '{}'
                    WHERE be_curp = '{}'
                    """.format(values[1],values[2],values[3],values[4],values[5],values[6],values[7],values[0]))
        ##return {'query': str(query)}


api.add_resource(Curps, '/Curps') # Route_1
api.add_resource(Registros, '/Registros') # Route_2
api.add_resource(BenfsData, '/Curps/<be_curp>') # Route_3
api.add_resource(Create_new_register, '/new_curp_reg')
api.add_resource(Delete_Register, '/Del_Reg') #Route_5
api.add_resource(Edit_Register, '/Edit/<be_curp>')

if __name__ == '__main__':
     app.run(port='5002')