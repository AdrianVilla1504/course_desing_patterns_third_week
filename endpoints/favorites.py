from flask_restful import Resource, reqparse
from flask import request
from utils.database_connection import DatabaseConnection
from utils.authenticator import create_authenticator  # Importando la función de creación de autenticador

# Refactorización de la clase FavoritesResource para usar la misma lógica de autenticación
class FavoritesResource(Resource):
    def __init__(self):
        # Conexión a la base de datos de favoritos
        self.db = DatabaseConnection('db.json')  # Base de datos de favoritos
        self.db.connect()

        # Recuperación de los datos de favoritos
        self.favorites = self.db.get_favorites()

        # Inicializa el parser para manejar los parámetros de la solicitud
        self.parser = reqparse.RequestParser()

    def get(self):
        """Obtiene la lista de favoritos del usuario."""
        authenticator = create_authenticator()  # Creación del objeto Authenticator utilizando la fábrica.
        auth_result = authenticator.authenticate()  # Autenticación con el patrón Estrategia.
        if auth_result:
            return auth_result  # Si la autenticación falla, devuelve el mensaje de error.

        # Devuelve los favoritos desde la base de datos
        return self.db.get_favorites(), 200

    def post(self):
        """Agrega un producto a los favoritos del usuario."""
        authenticator = create_authenticator()  # Creación del objeto Authenticator utilizando la fábrica.
        auth_result = authenticator.authenticate()  # Autenticación con el patrón Estrategia.
        if auth_result:
            return auth_result  # Si la autenticación falla, devuelve el mensaje de error.

        # Define los parámetros necesarios para la solicitud
        self.parser.add_argument('user_id', type=int, required=True, help='User ID')
        self.parser.add_argument('product_id', type=int, required=True, help='Product ID')

        args = self.parser.parse_args()
        new_favorite = {
            'user_id': args['user_id'],
            'product_id': args['product_id']
        }

        # Agrega el nuevo favorito a la lista y a la base de datos
        self.favorites.append(new_favorite)
        self.db.add_favorite(new_favorite)
        
        return {'message': 'Product added to favorites', 'favorite': new_favorite}, 201

    def delete(self):
        """Elimina un producto de los favoritos del usuario."""
        authenticator = create_authenticator()  # Creación del objeto Authenticator utilizando la fábrica.
        auth_result = authenticator.authenticate()  # Autenticación con el patrón Estrategia.
        if auth_result:
            return auth_result  # Si la autenticación falla, devuelve el mensaje de error.

        # Define los parámetros necesarios para la solicitud
        self.parser.add_argument('user_id', type=int, required=True, help='User ID')
        self.parser.add_argument('product_id', type=int, required=True, help='Product ID')

        args = self.parser.parse_args()
        user_id = args['user_id']
        product_id = args['product_id']

        # Encuentra y elimina el producto de favoritos
        self.favorites = [favorite for favorite in self.favorites
                          if not (favorite['user_id'] == user_id and favorite['product_id'] == product_id)]
        self.db.save_favorites(self.favorites)

        return {'message': 'Product removed from favorites'}, 200
