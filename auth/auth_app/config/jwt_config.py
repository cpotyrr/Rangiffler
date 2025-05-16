import os
from auth_app.security.jwks import generate_keys

# Generate RSA keys for JWKS
keys = generate_keys()
JWT_PRIVATE_KEY = keys['private_key']
JWT_PUBLIC_KEY = keys['public_key']
JWT_JWK = keys['jwk']
JWT_ALGORITHM = "RS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# OAuth2 settings
OAUTH2_TOKEN_URL = "token" 