from flask_restful import Resource, reqparse
from utils.database_connection import DatabaseConnection
from utils.authenticator import create_authenticator

# Fachada para acceder a la base de datos de categorías
class CategoriesFacade:
    def __init__(self):
        self.db = DatabaseConnection('db.json')
        self.db.connect()
        self.categories_data = self.db.get_categories()

    def get_category_by_id(self, category_id):
        """Obtiene una categoría por su ID."""
        return next((cat for cat in self.categories_data if cat['id'] == category_id), None)

    def get_all_categories(self):
        """Obtiene todas las categorías."""
        return self.categories_data

    def add_category(self, category_data):
        """Agrega una nueva categoría a la base de datos."""
        self.categories_data.append(category_data)
        self.db.add_category(category_data)

    def remove_category(self, category_name):
        """Elimina una categoría de la base de datos."""
        self.categories_data = [cat for cat in self.categories_data if cat['name'] != category_name]
        self.db.remove_category(category_name)

# Refactorización de la clase CategoriesResource para usar la fachada
class CategoriesResource(Resource):
    def __init__(self):
        # Instanciamos la fachada de categorías
        self.facade = CategoriesFacade()

        # Inicializamos el parser para manejar los parámetros de las solicitudes
        self.parser = reqparse.RequestParser()

    def get(self, category_id=None):
        """Obtiene las categorías."""
        authenticator = create_authenticator()  # Creación del objeto Authenticator utilizando la fábrica.
        auth_result = authenticator.authenticate()  # Autenticación con el patrón Estrategia.
        if auth_result:
            return auth_result

        # Buscar categoría específica si se proporciona un ID
        if category_id is not None:
            category = self.facade.get_category_by_id(category_id)  # Usamos la fachada para obtener la categoría
            if category:
                return category
            else:
                return {'message': 'Category not found'}, 404

        return self.facade.get_all_categories()  # Usamos la fachada para obtener todas las categorías

    def post(self):
        """Agrega una nueva categoría."""
        authenticator = create_authenticator()  # Creación del objeto Authenticator utilizando la fábrica.
        auth_result = authenticator.authenticate()  # Autenticación con el patrón Estrategia.
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
        if any(cat['name'] == new_category_name for cat in self.facade.categories_data):
            return {'message': 'Category already exists'}, 400

        # Crear una nueva categoría
        new_category = {'id': len(self.facade.categories_data) + 1, 'name': new_category_name}
        self.facade.add_category(new_category)  # Usamos la fachada para agregar la categoría

        return {'message': 'Category added successfully'}, 201

    def delete(self):
        """Elimina una categoría."""
        authenticator = create_authenticator()  # Creación del objeto Authenticator utilizando la fábrica.
        auth_result = authenticator.authenticate()  # Autenticación con el patrón Estrategia.
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
        category_to_remove = next((cat for cat in self.facade.categories_data if cat["name"] == category_name), None)
        if not category_to_remove:
            return {'message': 'Category not found'}, 404

        # Eliminar categoría de la lista y la base de datos
        self.facade.remove_category(category_name)  # Usamos la fachada para eliminar la categoría

        return {'message': 'Category removed successfully'}, 200