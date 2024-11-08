import pika
import time
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

# Carregar a chave privada para assinar as mensagens
with open("private_key2.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
    )

# Função para assinar uma mensagem
def sign_message(message):
    signature = private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

# Configuração do RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='orders', exchange_type='topic')

# Função para publicar uma solicitação de compra
def publish_purchase_order(asset, quantity):
    message = f"Compra {quantity} de {asset}"
    signature = sign_message(message)
    channel.basic_publish(
        exchange='orders',
        routing_key=f'order.{asset}',
        body=message.encode() + b'|' + signature
    )

# Exemplo de publicação de uma solicitação de compra
asset = 'btc'
quantity = 1
publish_purchase_order(asset, quantity)
print(f"Publicado: Compra de {quantity} de {asset}")

connection.close()
