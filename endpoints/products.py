from flask_restful import Resource, reqparse
from flask import request
from utils.database_connection import DatabaseConnection
from utils.authenticator import create_authenticator

# Fachada para manejar la base de datos de productos
class ProductFacade:
    def __init__(self):
        self.db = DatabaseConnection('db.json')  # Conexión a la base de datos.
        self.db.connect()
        self.products = self.db.get_products()

    def get_product_by_id(self, product_id):
        """Obtiene un producto por su ID."""
        return next((p for p in self.products if p['id'] == product_id), None)

    def filter_products_by_category(self, category):
        """Filtra productos por categoría."""
        return [p for p in self.products if p['category'].lower() == category.lower()]

    def add_product(self, product_data):
        """Agrega un nuevo producto a la base de datos."""
        self.products.append(product_data)
        self.db.add_product(product_data)

# Refactorización de la clase ProductsResource para usar la fachada y la autenticación.
class ProductsResource(Resource):
    def __init__(self):
        # Instancia la fachada para simplificar operaciones relacionadas con productos.
        self.facade = ProductFacade()

        # Inicializa el parser para manejar los parámetros de la solicitud.
        self.parser = reqparse.RequestParser()

    def get(self, product_id=None):
        """Obtiene productos o un producto específico."""
        authenticator = create_authenticator()  # Creación del objeto Authenticator utilizando la fábrica.
        auth_result = authenticator.authenticate()  # Autenticación con el patrón Estrategia.
        if auth_result:
            return auth_result

        # Si se proporciona un ID de producto, se obtiene el producto específico.
        if product_id is not None:
            product = self.facade.get_product_by_id(product_id)  # Usamos la fachada para obtener el producto
            if product:
                return product
            else:
                return {'message': 'Product not found'}, 404

        # Si no se especifica un ID de producto, devuelve todos los productos.
        return self.facade.products  # Devuelve todos los productos

    def post(self):
        """Agrega un nuevo producto."""
        authenticator = create_authenticator()  # Creación del objeto Authenticator utilizando la fábrica.
        auth_result = authenticator.authenticate()  # Autenticación con el patrón Estrategia.
        if auth_result:
            return auth_result

        # Define los parámetros esperados para la solicitud.
        self.parser.add_argument('name', type=str, required=True, help='Name of the product')
        self.parser.add_argument('category', type=str, required=True, help='Category of the product')
        self.parser.add_argument('price', type=float, required=True, help='Price of the product')

        # Parsea los argumentos de la solicitud.
        args = self.parser.parse_args()

        # Crea el nuevo producto.
        new_product = {
            'id': len(self.facade.products) + 1,
            'name': args['name'],
            'category': args['category'],
            'price': args['price']
        }

        # Usa la fachada para agregar el producto.
        self.facade.add_product(new_product)

        # Retorna una respuesta indicando que el producto fue agregado correctamente.
        return {'message': 'Product added', 'product': new_product}, 201