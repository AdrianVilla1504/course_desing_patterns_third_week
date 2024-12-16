from flask import Blueprint, request
from flask_restful import Resource, Api

# Estrategia de autenticación
class AuthenticationStrategy:
    def authenticate(self, username, password):
        if username == 'student' and password == 'desingp':
            return 'abcd12345'  # Token válido
        return None  # No autorizado

# Recurso de autenticación
class AuthenticationResource(Resource):
    def __init__(self):
        self.authenticator = AuthenticationStrategy()  # Se inyecta la estrategia de autenticación

    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')

        token = self.authenticator.authenticate(username, password)  # Usamos la estrategia para autenticar
        if token:
            return {'token': token}, 200
        else:
            return {'message': 'unauthorized'}, 401
