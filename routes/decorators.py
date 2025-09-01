# Decorators routes - RU 4493981
from functools import wraps # Para preservar assinatura da função decorada
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(*roles):
    """
    Decorator para restringir o acesso a rotas baseado na role do usuário.
    
    Parâmetros:
        roles: uma ou mais roles permitidas para acessar a rota.
    
    Como funciona:
    - Verifica se o usuário possui um token JWT válido.
    - Recupera a role do token.
    - Se a role não estiver entre as permitidas, retorna 403.
    - Caso contrário, executa a função original.
    
    Uso:
        @role_required("admin")
        def minha_rota():
            pass
    """
    def wrapper(fn):
        @wraps(fn) # Mantém nome e docstring da função original
        def decorated(*args, **kwargs):
            # Verifica se há JWT válido na requisição
            verify_jwt_in_request()

            # Obtém os claims (informações adicionais) do token
            claims = get_jwt()
            role = claims.get("role") # Recupera a role do usuário

            # Se a role não estiver entre as permitidas, bloqueia o acesso
            if role not in roles:
                return jsonify({
                    "msg": "Acesso negado", 
                    "required": roles, # Roles esperadas
                    "role": role # Role atual do usuário
                    }), 403
            
            # Executa a função original se a role estiver permitida
            return fn(*args, **kwargs)
        return decorated
    return wrapper
