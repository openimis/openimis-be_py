from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import jwt
import requests
import json
import os
from django.conf import settings

@csrf_exempt
@require_http_methods(["GET", "POST"])
def validate_jwt_for_opensearch(request):
    """
    Endpoint pour valider les tokens JWT pour OpenSearch
    Utilisé par nginx auth_request
    """
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return HttpResponse(status=401)
    
    token = auth_header.replace('Bearer ', '')
    
    try:
        # Valider le token JWT avec Keycloak
        keycloak_server_url = getattr(settings, 'KEYCLOAK_SERVER_URL', 'http://localhost:8080')
        keycloak_realm = getattr(settings, 'KEYCLOAK_REALM', 'openimis')
        
        # Obtenir la clé publique de Keycloak
        certs_url = f"{keycloak_server_url}/realms/{keycloak_realm}/protocol/openid_connect/certs"
        response = requests.get(certs_url)
        if response.status_code != 200:
            return HttpResponse(status=401)
        
        keys = response.json()['keys']
        
        # Décoder le token JWT
        header = jwt.get_unverified_header(token)
        key_id = header.get('kid')
        
        # Trouver la bonne clé
        public_key = None
        for key in keys:
            if key['kid'] == key_id:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break
        
        if not public_key:
            return HttpResponse(status=401)
        
        # Valider le token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=getattr(settings, 'KEYCLOAK_CLIENT_ID', 'openimis-frontend'),
            issuer=f"{keycloak_server_url}/realms/{keycloak_realm}"
        )
        
        # Extraire les informations utilisateur
        username = payload.get('preferred_username', '')
        roles = payload.get('realm_access', {}).get('roles', [])
        
        # Préparer la réponse avec les headers pour nginx
        response = HttpResponse(status=200)
        response['X-User'] = username
        response['X-Roles'] = ','.join(roles)
        response['X-JWT-Token'] = auth_header  # Passer le token JWT complet
        
        return response
        
    except jwt.ExpiredSignatureError:
        return HttpResponse(status=401)
    except jwt.InvalidTokenError:
        return HttpResponse(status=401)
    except Exception as e:
        print(f"JWT validation error: {e}")
        return HttpResponse(status=401)