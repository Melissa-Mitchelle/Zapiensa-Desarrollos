import time

import requests
from flask import Flask, \
    render_template, send_from_directory, request, url_for, redirect, make_response, session, jsonify, flash, send_file, \
    stream_with_context, Response
from datetime import timedelta, date, datetime

from werkzeug.datastructures import ImmutableMultiDict, Headers

app = Flask(__name__)
app.secret_key = 'ZAP/IENSA'
apiURL = "localhost:5002"
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
                      'message': "Mensaje"
                      }


def verify_session(fn):
    def inner(*args, **kwargs):
        if not 'role' in session:
            context = ''
            if '?' in request.url:
                context = request.url[(request.url.find('?') + 1):]
            return redirect(url_for('login') + '?siguiente=' + request.path + "?" + context)
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
        r = requests.put('http://' + apiURL + '/followUpdate/' + request.form['id_follow'],
                         json=payload,
                         headers={'Authentication-Token': session['api_session_token']}
                         )
        return r.text
    else:
        r = requests.post('http://' + apiURL + '/createFollow',
                          json=payload,
                          headers={'Authentication-Token': session['api_session_token']}
                          )
        return r.text


@app.route("/seguimientos")
@verify_session
def follows():
    r2 = requests.get('http://' + apiURL + '/follows', headers={'Authentication-Token': session['api_session_token']})
    return render_template('follows.html', receivers_follows=r2.json())


@app.route("/crearEvento", methods=['GET', 'POST'])
@verify_session
def create_event():
    if request.method == 'GET':
        return redirect('dataAdmin')
    payload = {
        key: value[0] if len(value) == 1 else value
        for key, value in request.form.items()
    }
    r = requests.post('http://' + apiURL + '/createEvent',
                      json=payload,
                      headers={'Authentication-Token': session['api_session_token']})
    if r.ok:
        flash(r.json()['message'])
        return redirect('dataAdmin')
    else:
        msgs = []
        if isinstance(r.json(), dict):
            for key, msge in r.json().items():
                if isinstance(msge, list):
                    for msg in msge:
                        msgs.append(fields_translation[key] + ": " + msg)
                else:
                    msgs.append(fields_translation[key] + ": " + msge)
        else:
            msgs.append(fields_translation[key] + ": " + r.json())
        return jsonify(success=0, msg=msgs), 500

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
            if payload['roles'] == '':
                return jsonify(success=0, msg=['Selecciona un rol para este usuario.'], url=""), 500

            payload['roles'] = int(payload['roles'])
        for key, value in payload.items():
            if value == "":
                payload[key] = None
        r = requests.post('http://' + apiURL + '/createUser',
                          json=payload,
                          headers={'Authentication-Token': session['api_session_token']}
                          )
        if r.ok:
            flash(r.json()['message'])
            return jsonify(success=1, msg=[str(r.json()['message'])],  url=""), 200
        else:
            msgs = []
            print(r.json())
            if isinstance(r.json(), dict):
                for key, msge in r.json().items():
                    if isinstance(msge, list):
                        for msg in msge:
                            msgs.append(fields_translation[key] + ": " + msg)
                    else:
                        msgs.append(fields_translation[key] + ": " + msge)
            else:
                msgs.append(fields_translation[key] + ": " + r.json())
        return jsonify(success=0, msg=msgs), 500


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    try:
        r = requests.get('http://' + apiURL + '/logout',
                         headers={'Authentication-Token': session['api_session_token']})
    except:
        pass

    session.clear()
    return redirect('/')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        response = make_response(render_template('login.html'))
        return response
    elif request.method == 'POST':
        payload = {'email': request.form['username'], 'password': request.form['password']}
        with requests.Session() as s:
            r = s.post('http://' + apiURL + '/login', json=payload)
            if r.ok:
                token = r.json()['response']['user']['authentication_token']
                session['api_session_token'] = token
                r2 = s.get('http://' + apiURL + '/checkrole')
                session['role'] = r2.text.replace('"', '').replace('\n', '').lower()
                if 'siguiente' in request.args:
                    return jsonify(success=1, msg=['Inicio de sesion exitoso'], url=request.args['siguiente']), 200
                else:
                    return jsonify(success=1, msg=['Inicio de sesion exitoso'], url='/dashboard'), 200
            else:
                print(r.json())
                """for e in r.json()['response']['errors']:
                    flash(r.json()['response']['errors'][e][0])"""
                return jsonify(success=0, msg=['Verifica que tu usuario y contraseña sean correctos.']), 403


@app.route("/crearBeneficiario", methods=['GET', 'POST'])
@verify_session
def create_receiver():
    if request.method == 'GET':
        re = requests.get('http://' + apiURL + '/checkEvents',
                          headers={'Authentication-Token': session['api_session_token']})
        return render_template('create_receiver.html', e_list=re.json())
    elif request.method == 'POST':
        payload = {
        }
        for key, value in request.form.items():
            if key == 'events':
                payload[key] = request.form.getlist(key)
            else:
                if len(value) == 1:
                    payload[key] = value[0]
                else:
                    payload[key] = value
        for key, value in payload.items():
            if value == "":
                payload[key] = None
        r = requests.post('http://' + apiURL + '/createReceiver',
                          json=payload,
                          headers={'Authentication-Token': session['api_session_token']}
                          )
        if r.ok:
            flash(r.json()['message'])
            return jsonify(success=1, msg=[r.json()['message']], url="")
        else:
            if r.headers.get('content-type') == "text/html; charset=utf-8":
                return jsonify(success=0, msg=r.text), 500
            else:
                msgs = []
                if isinstance(r.json(), dict):
                    for key, msge in r.json().items():
                        if isinstance(msge, list):
                            for msg in msge:
                                msgs.append(fields_translation[key] + ": " + msg)
                        else:
                            msgs.append(fields_translation[key] + ": " + msge)
                else:
                    msgs.append(fields_translation[key] + ": " + r.json())
            return jsonify(success=0, msg=msgs), 500


@app.route("/modificaciones", methods=['GET'])
@verify_session
def modifications():
    role = session['role']
    try:
        if role == 'administrador':
            r = requests.get('http://' + apiURL + '/receiversModifications',
                             headers={'Authentication-Token': session['api_session_token']})
            if r.ok:
                return render_template(role + '/modifications.html', receivers_modifications=r.json())
            elif r.status_code == 403:
                return redirect(url_for('login'))
            else:
                return r.content, 500
        else:
            return render_template(role + '/dashboard.html')
    except ValueError:
        return redirect(url_for('login'))


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def myround(x, base=5):
    return base * round(x/base)

@app.route("/dashboard", methods=['GET'])
@verify_session
def dashboard():
    role = session['role']
    try:
        if role == 'administrador':

            r = requests.get('http://' + apiURL + '/checkEvents',
                             headers={'Authentication-Token': session['api_session_token']})
            r2 = requests.get('http://' + apiURL + '/statistics',
                              headers={'Authentication-Token': session['api_session_token']})
            rawstats = r2.json()
            stats_spline = {}
            for event in rawstats['stats_spline']:
                if event not in stats_spline:
                    stats_spline[event] = {}
                    stats_spline[event]['attendance'] = {}
                    stats_spline[event]['unattendance'] = {}

                for rawdata in rawstats['stats_spline'][event]:
                    r_age = myround(calculate_age(datetime.strptime(rawdata['birthdate'], '%Y-%m-%d')))
                    if rawdata['attendance']:
                        if r_age not in stats_spline[event]['attendance']:
                            stats_spline[event]['attendance'][r_age] = {}
                            stats_spline[event]['attendance'][r_age]['M'] = 0
                            stats_spline[event]['attendance'][r_age]['H'] = 0
                        stats_spline[event]['attendance'][r_age][rawdata['gender']] += 1
                    else:
                        if r_age not in stats_spline[event]['unattendance']:
                            stats_spline[event]['unattendance'][r_age] = {}
                            stats_spline[event]['unattendance'][r_age]['M'] = 0
                            stats_spline[event]['unattendance'][r_age]['H'] = 0
                        stats_spline[event]['unattendance'][r_age][rawdata['gender']] += 1
            return render_template(role + '/dashboard.html', events=r.json(), stats_spline=stats_spline,
                                   total_assistants=rawstats['total_assistants'],
                                   users_follows=rawstats['users_follows'])
        else:
            return render_template(role + '/dashboard.html')
    except ValueError:
        print(ValueError.with_traceback())
        return redirect(url_for('login'))


@app.route("/buscar", methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        if 'curp' in request.args and 'role' not in session:
            curp = request.args['curp']
            r = requests.get('http://' + apiURL + '/CurpsGuest/' + curp)
            if r.ok:
                return render_template('anonymous_search_result.html', receivers=r.json())
            else:
                message = "No se encontro registro del CURP en ningun evento."
                flash(message)
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
            'http://' + apiURL + '/searchReceiver/' + search_type + '/' + request.form['search_data'],
            headers={'Authentication-Token': session['api_session_token']})
        if r.ok:
            return render_template('search_result.html', receivers=r.json())
        else:
            message = "No se encontraron registros."
            flash(message)
            return render_template('search.html')


@app.route("/modificacion", methods=['POST'])
@verify_session
def modificacion():
    if request.form['metodo'] == 'aprobar':
        r = requests.get('http://' + apiURL + '/approveReceiverModification/' + request.form['id'],
                         headers={'Authentication-Token': session['api_session_token']})
        if r.ok:
            return "Satisfactorio", 200
        else:
            return "Error", r.status_code
    elif request.form['metodo'] == 'cancelar':
        r = requests.get('http://' + apiURL + '/cancelReceiverModification/' + request.form['id'],
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
            r = requests.get('http://' + apiURL + '/receiver/' + request.args['id'],
                             headers={'Authentication-Token': session['api_session_token']})
            re = requests.get('http://' + apiURL + '/checkEvents',
                             headers={'Authentication-Token': session['api_session_token']})
            return render_template('edit_receiver.html', e_list=re.json(), receiver=r.json())
        else:
            return 'No se encontro el usuario.'
    elif request.method == 'POST':
        payload = {}
        for key, value in request.form.items():
            if key == 'events':
                payload[key] = request.form.getlist(key)
            else:
                if len(value) == 1:
                    payload[key] = value[0]
                else:
                    payload[key] = value
        for key, value in payload.items():
            if value == "":
                payload[key] = None

        r = None
        if session['role'] == "administrador":
            payload.pop('id_receiver')
            r = requests.put('http://' + apiURL + '/editReceiver/' + request.args['id'],
                             json=payload,
                             headers={'Authentication-Token': session['api_session_token']}
                             )
        elif session['role'] == "validador":
            r = requests.post('http://' + apiURL + '/createReceiverMirror',
                              json=payload,
                              headers={'Authentication-Token': session['api_session_token']}
                              )

        if r.ok:
            return jsonify(success=1, msg=['Registro actualizado.'])
        else:
            print(r.headers.get('content-type'))
            if r.headers.get('content-type') == "text/html; charset=utf-8":
                return jsonify(success=0, msg=r.text), 500
            else:
                msgs = []
                if isinstance(r.json(), dict):
                    for key, msge in r.json().items():
                        if isinstance(msge, list):
                            for msg in msge:
                                msgs.append(fields_translation[key] + ": " + msg)
                        else:
                            msgs.append(fields_translation[key] + ": " + msge)
                else:
                    msgs.append(fields_translation[key] + ": " + r.json())
            return jsonify(success=0, msg=msgs), 500



@app.route("/dataAdmin", methods=['GET', 'POST'])
@verify_session
def data_admin():
    r = requests.get('http://' + apiURL + '/checkEvents',
                     headers={'Authentication-Token': session['api_session_token']})
    return render_template('administrador/data_admin.html', una_lista=['Tipo ZAP Academy', 'Tipo Apoyo a Mujeres',
                                                                       'Tipo Jalisco te Reconoce', 'Otro Tipo'],
                           fecha=time.strftime("%Y%m%d-%H%M%S"), e_list=r.json())


@app.route("/importar", methods=['POST'])
@verify_session
def importar():
    data = request.files
    bin_file = data.get('fileimported')
    print(bin_file)
    data_file = {"fileimported": (bin_file.filename, bin_file.read(), bin_file.content_type)}
    print(data_file)
    re = requests.get('http://' + apiURL + '/checkEvents',
                     headers={'Authentication-Token': session['api_session_token']})
    r = requests.post('http://' + apiURL + '/importation', data={'tipo': request.form['tipo'], 'e_name': request.form['e_name']}, files=data_file,
                      verify=False, headers={'Authentication-Token': session['api_session_token']})
    if r.ok:
        flash('Listo.')
    else:
        flash(r.content)
    return render_template('administrador/data_admin.html', e_list=re.json(), una_lista=['Tipo ZAP Academy', 'Tipo Apoyo a Mujeres',
                                                                       'Tipo Jalisco te Reconoce', 'Otro Tipo'],
                           fecha=time.strftime("%Y%m%d-%H%M%S"))


@app.route("/exportar", methods=['GET'])
@verify_session
def exportar():
    r = requests.get('http://' + apiURL + '/exports?filename=' + request.args['fecha'], stream=True,
                     headers={'Authentication-Token': session['api_session_token']})

    headers = Headers()
    headers.add_header('Content-Type', r.headers["content-type"])
    headers.add_header('Content-Disposition',
                       'attachment; filename="' + 'exportacion-' + time.strftime("%Y%m%d-%H%M%S") + '.xls"')
    return Response(stream_with_context(r.iter_content(chunk_size=2048)), headers=headers)


@app.route("/respaldo", methods=['GET'])
@verify_session
def respaldo():
    r = requests.get('http://' + apiURL + '/backup', stream=True,
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
