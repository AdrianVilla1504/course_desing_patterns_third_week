from flask_restful import Resource, reqparse
from flask import request
from utils.database_connection import DatabaseConnection
from utils.authenticator import create_authenticator  # Importando la función de creación de autenticador

# Adaptador para el validador de tokens
class TokenValidatorAdapter:
    def __init__(self, authenticator):
        self.authenticator = authenticator

    def is_valid(self, token: str) -> bool:
        # Usamos el autenticador para validar el token
        response = self.authenticator.authenticate()
        return response is None  # Si no hay errores, el token es válido

# Refactorización de la clase FavoritesResource para usar el patrón Adapter
class FavoritesResource(Resource):
    def __init__(self):
        self.db = DatabaseConnection('favorites.json')
        self.db.connect()

        self.favorites = self.db.get_favorites()

        # Creamos el autenticador y adaptamos su interfaz para usarla en lugar de la validación directa
        authenticator = create_authenticator()
        self.token_validator = TokenValidatorAdapter(authenticator)

    def get(self):
        token = request.headers.get('Authorization')

        # Usamos el adaptador para validar el token
        if not token or not self.token_validator.is_valid(token):
            return {'message': 'Unauthorized access token not found or invalid'}, 401

        return self.db.get_favorites(), 200

    def post(self):
        token = request.headers.get('Authorization')
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True, help='User ID')
        parser.add_argument('product_id', type=int, required=True, help='Product ID')

        # Usamos el adaptador para validar el token
        if not token or not self.token_validator.is_valid(token):
            return {'message': 'Unauthorized access token not found or invalid'}, 401

        args = parser.parse_args()
        new_favorite = {
            'user_id': args['user_id'],
            'product_id': args['product_id']
        }

        self.favorites.append(new_favorite)
        self.db.add_favorite(new_favorite)
        return {'message': 'Product added to favorites', 'favorite': new_favorite}, 201

    def delete(self):
        token = request.headers.get('Authorization')
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True, help='User ID')
        parser.add_argument('product_id', type=int, required=True, help='Product ID')

        # Usamos el adaptador para validar el token
        if not token or not self.token_validator.is_valid(token):
            return {'message': 'Unauthorized access token not found or invalid'}, 401

        args = parser.parse_args()
        user_id = args['user_id']
        product_id = args['product_id']

        # Encuentra y elimina el producto de favoritos
        self.favorites = [favorite for favorite in self.favorites
                          if not (favorite['user_id'] == user_id and favorite['product_id'] == product_id)]
        self.db.save_favorites(self.favorites)

        return {'message': 'Product removed from favorites'}, 200
