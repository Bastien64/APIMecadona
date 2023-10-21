import unittest
import json
from app import app, db
import os
import base64

image_path = os.path.join(os.path.dirname(__file__), 'image.jpg')
with open(image_path, 'rb') as image_file:
    image_data = image_file.read()
image_base64 = base64.b64encode(image_data).decode('utf-8')  


class TestYourAPI(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
       
        pass

    def test_login_admin(self):
        data = {
            'login': 'admin_username',
            'password': 'admin_password'
        }
        response = self.app.post('/admin', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_create_admin(self):
        data = {
            'login': 'new_admin',
            'password': 'new_password'
        }
        response = self.app.post('/admin/create', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_get_produits(self):
        response = self.app.get('/produit')
        self.assertEqual(response.status_code, 200)

    def test_create_produit(self):
        data = {
            'description': 'Nouveau produit',
            'price': 99,
            'image': 'data:image/jpeg;base64,' + image_base64,
            'categorie_id': 1
        }
        response = self.app.post('/produit', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_get_categories(self):
        response = self.app.get('/categorie')
        self.assertEqual(response.status_code, 200)

    def test_get_promotions(self):
        response = self.app.get('/promotion')
        self.assertEqual(response.status_code, 200)

    def test_add_promotion(self):
        data = {
            'datedebut': '2023-01-01',
            'datefin': '2023-02-01',
            'pourcentage': 10,
            'produit_id': 1
        }
        response = self.app.post('/promotion', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()