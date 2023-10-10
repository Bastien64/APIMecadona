import os
import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Utilisez os.environ.get pour obtenir le port de l'environnement Heroku
port = int(os.environ.get('PORT', 5000))

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Hello World</h1>'''

@app.route("/login",  methods=['POST'])
def convert():
    user = request.get_json()
    if user['username'] == 'admin' and user['password'] == '1234':
        return jsonify({'success': True, 'message': 'Valid user'})
    return jsonify({'success': False, 'message': 'Invalid user'})

if __name__ == '__main__':
    # Utilisez le port défini par Heroku (via os.environ.get)
    app.run(host="0.0.0.0", port=port)
