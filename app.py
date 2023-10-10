import os
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
import base64
import bcrypt
from flask_cors import CORS
from werkzeug.serving import WSGIRequestHandler
import io  # Importez le module io
from PIL import Image  # Importez la bibliothèque PIL pour vérifier le type de l'image
from sqlalchemy.dialects.postgresql import NUMERIC
from sqlalchemy.dialects.postgresql import BYTEA  # Utilisez le type BYTEA pour stocker des images binaires

from base64 import b64decode
WSGIRequestHandler.protocol_version = "HTTP/1.1"

app = Flask(__name__)

# Utilisez os.environ.get pour obtenir le port de l'environnement Heroku
port = int(os.environ.get('PORT', 5000))

CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456Azerty!@37.187.39.204/studi'

db = SQLAlchemy(app)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(BYTEA, nullable=False)  # Utilisez BYTEA pour stocker les images
    categorie_id = db.Column(db.Integer, nullable=False)


class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(255), nullable=False)

class Promotion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datedebut = db.Column(db.Date, nullable=False)
    datefin = db.Column(db.Date, nullable=False)
    pourcentage = db.Column(db.Float, nullable=False)
    produit_id = db.Column(db.Integer, nullable=False)

@app.route('/admin', methods=['GET', 'POST'])
def login_admin():
    login = request.json.get('login')
    password = request.json.get('password')

    admin = Admin.query.filter_by(login=login).first()

    if admin:
        hashed_password = admin.password.encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            admin_data = {
                'id': admin.id,
                'login': admin.login
            }
            return jsonify(admin_data), 200
        else:
            return "Unauthorized", 401
    else:
        return "Unauthorized", 401

@app.route('/admin/create', methods=['POST'])
def create_admin():
    login = request.json.get('login')
    password = request.json.get('password')

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_admin = Admin(login=login, password=hashed_password)

    db.session.add(new_admin)
    db.session.commit()

    return "Admin created successfully", 201

@app.route('/produit', methods=['GET'])
def get_produits():
    produits = Produit.query.all()
    produits_data = []

    for produit in produits:
        # Convertir le champ "image" en une chaîne base64
        image_base64 = base64.b64encode(produit.image).decode('utf-8')

        # Ajoutez le préfixe 'data:image/jpeg;base64,' à l'image
        image_base64_with_prefix = 'data:image/jpeg;base64,' + image_base64

        produit_data = {
            'id': produit.id,
            'description': produit.description,
            'price': produit.price,  # Convertir le price en chaîne de caractères
            'image': image_base64_with_prefix,  # Champ "image" avec préfixe
            'categorie_id': produit.categorie_id
        }
        produits_data.append(produit_data)

    return jsonify(produits_data)




@app.route('/produit', methods=['POST'])
def create_produit():
    description = request.json.get('description')
    price = request.json.get('price')
    image_base64 = request.json.get('image')  # Récupérez l'image en base64
    categorie_id = request.json.get('categorie_id')  # Récupérez categorie_id
    # Vérifiez si l'image contient déjà le préfixe 'data:image/jpeg;base64,'
    if not image_base64.startswith('data:image/jpeg;base64,'):
        image_base64 = 'data:image/jpeg;base64,' + image_base64

    # Supprimez le préfixe pour obtenir les données brutes en base64
    image_data = image_base64.replace('data:image/jpeg;base64,', '')

    # Convertissez les données base64 en bytes
    image_bytes = b64decode(image_data)

    new_produit = Produit(description=description, price=price, image=image_bytes, categorie_id=categorie_id)

    db.session.add(new_produit)
    db.session.commit()

    return "Produit créé avec succès", 201


@app.route('/categorie', methods=['GET'])
def get_categories():
    categories = Categorie.query.all()
    categories_data = []

    for categorie in categories:
        categorie_data = {
            'id': categorie.id,
            'libelle': categorie.libelle
        }
        categories_data.append(categorie_data)

    return jsonify(categories_data)

@app.route('/promotion', methods=['GET'])
def get_promotions():
    promotions = Promotion.query.all()
    promotions_data = []

    for promotion in promotions:
        promotion_data = {
            'id': promotion.id,
            'datedebut': promotion.datedebut.strftime('%Y-%m-%d'),
            'datefin': promotion.datefin.strftime('%Y-%m-%d'),
            'pourcentage': promotion.pourcentage,
            'produit_id': promotion.produit_id
        }
        promotions_data.append(promotion_data)

    return jsonify(promotions_data)

@app.route('/promotion', methods=['POST'])
def add_promotion():
    data = request.get_json()

    if 'datedebut' in data and 'datefin' in data and 'pourcentage' in data and 'produit_id' in data:
        datedebut = data['datedebut']
        datefin = data['datefin']
        pourcentage = data['pourcentage']
        produit_id = data['produit_id']

        new_promotion = Promotion(datedebut=datedebut, datefin=datefin, pourcentage=pourcentage, produit_id=produit_id)

        db.session.add(new_promotion)
        db.session.commit()

        return jsonify({"message": "La promotion a été ajoutée avec succès."}), 201
    else:
        return jsonify({"error": "Toutes les données nécessaires ne sont pas fournies."}), 400

if __name__ == '__main__':
    # Utilisez le port défini par Heroku (via os.environ.get)
    app.run(host="0.0.0.0", port=port)
