import json
from http import cookiejar
from urllib.parse import unquote

import requests
from flask import Flask, render_template, send_from_directory, request, url_for, redirect, make_response, session, Response

app = Flask(__name__)
app.secret_key = 'secret_key'


@app.route("/")
def index():
    return render_template('index.html')


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
                session['role'] = r2.text.replace('"','').replace('\n','')
                return redirect(url_for('dashboard_' + session['role'].lower()))
            else:
                return r.content


@app.route("/dashboard_administrador", methods=['GET'])
def dashboard_administrador():
    try:
        token = session['api_session_token']
        r = requests.get('http://localhost:5002/receiversModifications',
                         headers={'Authentication-Token': token})
        if r.ok:
            return render_template('dashboard_administrador.html', receivers_modifications=r.json())
        elif r.status_code == 403:
            return redirect(url_for('login'))
        else:
            return r.content, 500
    except ValueError:
        return redirect(url_for('login'))


@app.route("/dashboard_validador", methods=['GET'])
def dashboard_validador():
    try:
        return render_template('dashboard_validador.html')
    except ValueError:
        return redirect(url_for('login'))


@app.route("/search", methods=['GET'])
def search():
    curp = request.args['curp']
    if curp:
        r = requests.get('http://localhost:5002/CurpsGuest/' + curp)
        if r.ok:
            return render_template('search_result.html', receivers=r.json())
        else:
            return render_template('index.html', message=r.text)


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
    app.run(port='80')
