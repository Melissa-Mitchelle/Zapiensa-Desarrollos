from config import app
from flask import jsonify, render_template
from flask_security import login_required

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the API Server!'})


@app.route('/search')
@login_required
def search_form():
    return render_template('searchForm.html'), 200
