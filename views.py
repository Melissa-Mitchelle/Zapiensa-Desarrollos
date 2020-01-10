from run import app
from flask import jsonify, render_template


@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'})


@app.route('/search')
def search_form():
    return render_template('searchForm.html'), 200
