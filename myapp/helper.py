
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from django.contrib.auth.hashers import make_password
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .models import Token

# Encrypt private key using password key
def encrypt_private_key(private_key_pem,recovary_key):
    """Encrypt a private key using a given recovery key."""
    private_key = serialization.load_pem_private_key(private_key_pem.encode(),password=None)
    encrypted_private=private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(recovary_key)
    )
    return encrypted_private

def decrypt_private_key(encript_priver_key,password):
    """Decrypt a private key using a given recovery key."""
    private_key=serialization.load_pem_private_key(
        encript_priver_key,
        password=password
    )
    private_key_pem=private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()

    )
    return private_key_pem.decode('utf-8')



def generate_rsa_keys():
    """Generate RSA key pair and return (public_key, private_key)."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key=private_key.public_key()

    # Convert keys to PEM format
    private_key_pem=private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()

    )
    public_key_pem=public_key.public_bytes(
        encoding= serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return public_key_pem.decode('utf-8'), private_key_pem.decode('utf-8')



def encrypt_with_public_key(public_key_pem, data):
    """Encrypt data with a given public key."""
    pass

def decrypt_with_private_key():
    """Decrypt data with a given private key."""
    pass

def send_private_key_to_user(email,privet_key):
    """Send the private key to the user securely."""
    print(privet_key)

# Notify higher authorities for approval
def notify_higher_authorities(user):
    """Notify higher authorities for approval. Implement your notification logic here."""
    # Example: Send an email to the HoD or Dean for approval
    pass

def token_required(f):
    @wraps(f)
    def decorated(request, *args, **kwargs):
        token_key=request.headers.get("Authorization")
        if not token_key:
            return Response({'error': 'Token is missing'}, status=status.HTTP_401_UNAUTHORIZED)
        user = Token.verify_token(token_key)

        if not user :
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        request.user=user
        return f(request,*args, **kwargs)
    return decorated






