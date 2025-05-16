from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64
import json
from app.config.jwt_config import JWT_ALGORITHM

# Generate RSA key pair (this should be done once and stored securely in production)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

def int_to_base64(value: int) -> str:
    """Convert an integer to a base64url-encoded string"""
    value_hex = format(value, 'x')
    # Ensure even length
    if len(value_hex) % 2 == 1:
        value_hex = '0' + value_hex
    value_bytes = bytes.fromhex(value_hex)
    return base64.urlsafe_b64encode(value_bytes).rstrip(b'=').decode('ascii')

def get_jwks() -> dict:
    """Generate JWKS containing the public key"""
    public_numbers = public_key.public_numbers()
    
    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": "auth-key-1",  # Key ID
                "use": "sig",         # Signature
                "alg": JWT_ALGORITHM,
                "n": int_to_base64(public_numbers.n),  # Modulus
                "e": int_to_base64(public_numbers.e)   # Exponent
            }
        ]
    }

def get_private_key() -> rsa.RSAPrivateKey:
    """Get the private key for signing"""
    return private_key

def get_public_key() -> rsa.RSAPublicKey:
    """Get the public key for verification"""
    return public_key 