from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Gerar chave privada
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# Serializar e salvar a chave privada
with open("private_key.pem", "wb") as private_file:
    private_file.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Serializar e salvar a chave pública
public_key = private_key.public_key()
with open("public_key.pem", "wb") as public_file:
    public_file.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))
