import time

import requests
from flask import Flask, \
    render_template, send_from_directory, request, url_for, redirect, make_response, session, jsonify, flash, send_file, \
    stream_with_context, Response
from datetime import timedelta

from werkzeug.datastructures import ImmutableMultiDict, Headers

app = Flask(__name__)
app.secret_key = 'ZAP/IENSA'
app.permanent_session_lifetime = timedelta(minutes=15)
fields_translation = {'given_name': "Nombre",
                      'last_name': "Apellido Paterno",
                      's_last_name': "Apellido Materno",
                      'email': "Correo electronico",
                      'password': "Contraseña",
                      'username': "Nombre de usuario",
                      'curp': "CURP",
                      'zip_code': "Codigo Postal",
                      'address': "Dirección",
                      'p_phone': "Telefono 1",
                      'roles': "Roles",
                      }


def verify_session(fn):
    def inner(*args, **kwargs):
        if not 'role' in session:
            return redirect(url_for('login') + '?siguiente=' + request.path)
        return fn(*args, **kwargs)

    inner.__name__ = fn.__name__
    return inner


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/seguimiento", methods=['POST'])
@verify_session
def follow():
    payload = {
        key: value[0] if len(value) == 1 else value
        for key, value in request.form.items()
    }
    for key, value in payload.items():
        if value == "":
            payload[key] = None
    print(payload)
    if 'id_follow' in request.form:
        r = requests.put('http://localhost:5002/followUpdate/' + request.form['id_follow'],
                         json=payload,
                         headers={'Authentication-Token': session['api_session_token']}
                         )
        return r.text
    else:
        r = requests.post('http://localhost:5002/createFollow',
                          json=payload,
                          headers={'Authentication-Token': session['api_session_token']}
                          )
        return r.text


@app.route("/seguimientos")
@verify_session
def follows():
    r2 = requests.get('http://localhost:5002/follows', headers={'Authentication-Token': session['api_session_token']})
    return render_template('follows.html', receivers_follows=r2.json())


@app.route("/crearUsuario", methods=['GET', 'POST'])
@verify_session
def create_user():
    if request.method == 'GET':
        return render_template(session['role'] + '/create_user.html')
    if request.method == 'POST':
        payload = {
            key: value[0] if len(value) == 1 else value
            for key, value in request.form.items()
        }
        if 'roles' in payload:
            payload['roles'] = int(payload['roles'])
        for key, value in payload.items():
            if value == "":
                payload[key] = None
        print(payload)
        r = requests.post('http://localhost:5002/createUser',
                          json=payload,
                          headers={'Authentication-Token': session['api_session_token']}
                          )
        if r.ok:
            flash(r.json()['message'])
            return render_template(session['role'] + '/create_user.html')
        else:
            for e in r.json():
                flash(r.json()[e][0] + ' ' + fields_translation[e])
            return render_template(session['role'] + '/create_user.html')


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    r = requests.get("http://localhost:5002/logout",
                     headers={'Authentication-Token': session['api_session_token']})
    session.pop('role')
    session.pop('api_session_token')
    return redirect('/')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        response = make_response(render_template('login.html'))
        return response
    elif request.method == 'POST':
        payload = {'email': request.form['username'], 'password': request.form['password']}
        with requests.Session() as s:
            r = s.post('http://localhost:5002/login', json=payload)
            if r.ok:
                token = r.json()['response']['user']['authentication_token']
                session['api_session_token'] = token
                r2 = s.get('http://localhost:5002/checkrole')
                session['role'] = r2.text.replace('"', '').replace('\n', '').lower()
                if 'siguiente' in request.args:
                    return redirect(request.args['siguiente'])
                else:
                    return redirect('/dashboard')
            else:
                print(r.json())
                """for e in r.json()['response']['errors']:
                    flash(r.json()['response']['errors'][e][0])"""
                return render_template('login.html')


@app.route("/crearBeneficiario", methods=['GET', 'POST'])
@verify_session
def create_receiver():
    if request.method == 'GET':
        return render_template('create_receiver.html')
    elif request.method == 'POST':
        payload = {
            key: value[0] if len(value) == 1 else value
            for key, value in request.form.items()
        }
        for key, value in payload.items():
            if value == "":
                payload[key] = None
        r = requests.post('http://localhost:5002/createReceiver',
                          json=payload,
                          headers={'Authentication-Token': session['api_session_token']}
                          )
        if r.ok:
            flash(r.json()['message'])
            return render_template('create_receiver.html')
        else:
            for e in r.json():
                flash(r.json()[e][0] + ' ' + fields_translation[e])
            return render_template('create_receiver.html')


@app.route("/dashboard", methods=['GET'])
@verify_session
def dashboard_validador():
    role = session['role']
    try:
        if role == 'administrador':
            r = requests.get('http://localhost:5002/receiversModifications',
                             headers={'Authentication-Token': session['api_session_token']})
            if r.ok:
                return render_template(role + '/dashboard.html', receivers_modifications=r.json())
            elif r.status_code == 403:
                return redirect(url_for('login'))
            else:
                return r.content, 500
        else:
            return render_template(role + '/dashboard.html')
    except ValueError:
        return redirect(url_for('login'))


@app.route("/buscar", methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        if 'curp' in request.args and 'role' not in session:
            curp = request.args['curp']
            r = requests.get('http://localhost:5002/CurpsGuest/' + curp)
            if r.ok:
                return render_template('anonymous_search_result.html', receivers=r.json())
            else:
                flash(r.text)
                return render_template('index.html')
        elif 'role' in session:
            return render_template('search.html')
        else:
            return render_template('index.html')


    elif request.method == 'POST':
        if 'search_type' in request.form:
            search_type = request.form['search_type']
        else:
            search_type = "general"
        r = requests.get(
            'http://localhost:5002/searchReceiver/' + search_type + '/' + request.form['search_data'],
            headers={'Authentication-Token': session['api_session_token']})
        if r.ok:
            return render_template('search_result.html', receivers=r.json())
        else:
            flash(r.json()['message'])
            return render_template('search.html')


@app.route("/modificacion", methods=['POST'])
@verify_session
def modificacion():
    if request.form['metodo'] == 'aprobar':
        r = requests.get('http://localhost:5002/approveReceiverModification/' + request.form['id'],
                         headers={'Authentication-Token': session['api_session_token']})
        if r.ok:
            return "Satisfactorio", 200
        else:
            return "Error", r.status_code
    elif request.form['metodo'] == 'cancelar':
        r = requests.get('http://localhost:5002/cancelReceiverModification/' + request.form['id'],
                         headers={'Authentication-Token': session['api_session_token']})
        if r.ok:
            return "Satisfactorio", 200
        else:
            return "Error", r.status_code


@app.route("/editarBeneficiario", methods=['GET', 'POST'])
@verify_session
def edit_receiver():
    if request.method == 'GET':
        if 'id' in request.args:
            r = requests.get('http://localhost:5002/receiver/' + request.args['id'],
                             headers={'Authentication-Token': session['api_session_token']})
            return render_template('edit_receiver.html', receiver=r.json())
        else:
            return 'No se encontro el usuario.'
    elif request.method == 'POST':
        payload = {
            key: value[0] if len(value) == 1 else value
            for key, value in request.form.items()
        }
        for key, value in payload.items():
            if value == "":
                payload[key] = None
        if session['role'] == "administrador":
            payload.pop('id_receiver')
            r = requests.put('http://localhost:5002/editReceiver/' + request.args['id'],
                             json=payload,
                             headers={'Authentication-Token': session['api_session_token']}
                             )
        elif session['role'] == "validador":
            r = requests.post('http://localhost:5002/createReceiverMirror',
                              json=payload,
                              headers={'Authentication-Token': session['api_session_token']}
                              )
        flash(r.json()['message'])
        return render_template('search.html')


@app.route("/dataAdmin", methods=['GET', 'POST'])
@verify_session
def data_admin():
    return render_template('administrador/data_admin.html', una_lista=['Tipo ZAP Academy', 'Tipo Apoyo a Mujeres',
                                                                       'Tipo Jalisco te Reconoce', 'Otro Tipo'],
                           fecha=time.strftime("%Y%m%d-%H%M%S"))


@app.route("/importar", methods=['POST'])
@verify_session
def importar():
    data = request.files
    bin_file = data.get('fileimported')
    print(bin_file)
    data_file = {"fileimported": (bin_file.filename, bin_file.read(), bin_file.content_type)}
    print(data_file)
    r = requests.post('http://localhost:5002/importation', data={'tipo': request.form['tipo']}, files=data_file,
                      verify=False, headers={'Authentication-Token': session['api_session_token']})
    if r.ok:
        flash('Listo.')
    else:
        flash(r.content)
    return render_template('administrador/data_admin.html', una_lista=['Tipo ZAP Academy', 'Tipo Apoyo a Mujeres',
                                                                       'Tipo Jalisco te Reconoce', 'Otro Tipo'],
                           fecha=time.strftime("%Y%m%d-%H%M%S"))


@app.route("/exportar", methods=['GET'])
@verify_session
def exportar():
    r = requests.get('http://localhost:5002/exports?filename=' + request.args['fecha'], stream=True,
                     headers={'Authentication-Token': session['api_session_token']})

    headers = Headers()
    headers.add_header('Content-Type', r.headers["content-type"])
    headers.add_header('Content-Disposition',
                       'attachment; filename="' + 'exportacion-' + time.strftime("%Y%m%d-%H%M%S") + '.xls"')
    return Response(stream_with_context(r.iter_content(chunk_size=2048)), headers=headers)


@app.route("/respaldo", methods=['GET'])
@verify_session
def respaldo():
    r = requests.get('http://localhost:5002/backup', stream=True,
                     headers={'Authentication-Token': session['api_session_token']})

    headers = Headers()
    headers.add_header('Content-Type', r.headers["content-type"])
    headers.add_header('Content-Disposition',
                       'attachment; filename="' + 'respaldo-' + time.strftime("%Y%m%d-%H%M%S") + '.db"')
    return Response(stream_with_context(r.iter_content(chunk_size=2048)), headers=headers)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)


@app.route('/fonts/<path:path>')
def send_fs(path):
    return send_from_directory('static/fonts', path)


@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('static/img', path)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


if __name__ == '__main__':
    app.run(port='8080')
