from flask_restful import Resource, reqparse
from utils.database_connection import DatabaseConnection
from utils.authenticator import create_authenticator

class CategoriesResource(Resource):
    def __init__(self):
        # Instancia de conexión a la base de datos
        self.db = DatabaseConnection('db.json')
        self.db.connect()
        
        # Recuperación de datos de categorías
        self.categories_data = self.db.get_categories()

        # Inicializamos el parser para manejar los parámetros de las solicitudes
        self.parser = reqparse.RequestParser()

    def get(self, category_id=None):
        """Obtiene las categorías."""
        authenticator = create_authenticator()
        auth_result = authenticator.authenticate()
        if auth_result:
            return auth_result
        
        # Buscar categoría específica si se proporciona un ID
        if category_id is not None:
            category = next((cat for cat in self.categories_data if cat['id'] == category_id), None)
            if category:
                return category
            else:
                return {'message': 'Category not found'}, 404
        
        return self.categories_data

    def post(self):
        """Agrega una nueva categoría."""
        authenticator = create_authenticator()
        auth_result = authenticator.authenticate()
        if auth_result:
            return auth_result

        # Definir los argumentos necesarios para la solicitud
        self.parser.add_argument('name', type=str, required=True, help='Name of the category')
        args = self.parser.parse_args()
        new_category_name = args['name']

        # Validar nombre de categoría
        if not new_category_name:
            return {'message': 'Category name is required'}, 400

        # Verificar si la categoría ya existe
        if any(cat['name'] == new_category_name for cat in self.categories_data):
            return {'message': 'Category already exists'}, 400
        
        # Crear una nueva categoría
        new_category = {'id': len(self.categories_data) + 1, 'name': new_category_name}
        self.categories_data.append(new_category)
        self.db.add_category(new_category)

        return {'message': 'Category added successfully'}, 201

    def delete(self):
        """Elimina una categoría."""
        authenticator = create_authenticator()
        auth_result = authenticator.authenticate()
        if auth_result:
            return auth_result

        # Definir los argumentos para la solicitud
        self.parser.add_argument('name', type=str, required=True, help='Name of the category')
        args = self.parser.parse_args()
        category_name = args['name']

        # Validar nombre de categoría
        if not category_name:
            return {'message': 'Category name is required'}, 400

        # Buscar y eliminar la categoría
        category_to_remove = next((cat for cat in self.categories_data if cat["name"] == category_name), None)
        if not category_to_remove:
            return {'message': 'Category not found'}, 404

        # Eliminar categoría de la lista y la base de datos
        self.categories_data = [cat for cat in self.categories_data if cat["name"] != category_name]
        self.db.remove_category(category_name)

        return {'message': 'Category removed successfully'}, 200
