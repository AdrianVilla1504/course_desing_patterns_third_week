from flask import request
from abc import ABC, abstractmethod

# Interfaz para validadores de tokens - Aplicando el patrón Estrategia.
# La interfaz proporciona una forma de implementar diferentes estrategias de validación de token.
class TokenValidator(ABC):
    @abstractmethod
    def is_valid(self, token: str) -> bool:
        pass

# Implementación concreta de la validación del token - Estrategia concreta para la validación del token.
class StaticTokenValidator(TokenValidator):
    def is_valid(self, token: str) -> bool:
        return token == 'abcd12345'

# Clase encargada de la autenticación usando el patrón Estrategia
# La clase Authenticator toma una estrategia de validación de token y la usa para autenticar al usuario.
class Authenticator:
    def __init__(self, token_validator: TokenValidator):
        self.token_validator = token_validator

    def authenticate(self):
        """Autentica a un usuario mediante el token de acceso."""
        token = request.headers.get('Authorization')
        
        if not token:
            return {'message': 'Unauthorized access token not found'}, 401
        
        if not self.token_validator.is_valid(token):
            return {'message': 'Unauthorized invalid token'}, 401
        
        return None

# Función de fábrica para crear un objeto Authenticator con un validador
# Aplicando el patrón de fábrica para instanciar Authenticator con su estrategia de validación.
def create_authenticator():
    token_validator = StaticTokenValidator()  # Aquí estamos usando la estrategia concreta.
    return Authenticator(token_validator)
