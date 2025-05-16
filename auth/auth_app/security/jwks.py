from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import json
import base64

def generate_keys():
    # Generate RSA key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Get private key in PEM format
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Get public key in PEM format
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Get public key components for JWK
    numbers = public_key.public_numbers()
    e = base64.urlsafe_b64encode(numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, byteorder='big')).rstrip(b'=')
    n = base64.urlsafe_b64encode(numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, byteorder='big')).rstrip(b'=')

    return {
        'private_key': pem_private,
        'public_key': pem_public,
        'jwk': {
            'kty': 'RSA',
            'kid': '1',
            'n': n.decode('ascii'),
            'e': e.decode('ascii'),
            'alg': 'RS256',
            'use': 'sig'
        }
    }

def create_jwks(jwk):
    return {'keys': [jwk]} 