import pika
import time
import requests
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

# Carregar a chave privada para assinar as mensagens
with open("private_key.pem", "rb") as key_file:
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
channel.exchange_declare(exchange='assets', exchange_type='topic')

# Função para publicar uma mensagem assinada
def publish_asset_price(topic, message):
    signature = sign_message(message)
    channel.basic_publish(
        exchange='assets',
        routing_key=topic,
        body=message.encode() + b'|' + signature
    )

# Função para obter o preço do BTC
def get_btc_price():
     url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
     response = requests.get(url)
     data = response.json()
     return data["bitcoin"]["usd"]
    #  return 100000

# Função para obter o preço do ETH
def get_eth_price():
     url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
     response = requests.get(url)
     data = response.json()
     return data["ethereum"]["usd"]
    #  return 7000
# Publicação dos preços de BTC e ETH a cada 10 segundos
try:
    # No código do publicador:
    while True:
        # Obter e publicar preço do BTC
        btc_price = get_btc_price()
        message_btc = str(btc_price)  # Enviar apenas o valor numérico como string
        print(f"Publicando BTC: {message_btc}")
        publish_asset_price('asset.btc', message_btc)
        
        # Obter e publicar preço do ETH
        eth_price = get_eth_price()
        message_eth = str(eth_price)  # Enviar apenas o valor numérico como string
        print(f"Publicando ETH: {message_eth}")
        publish_asset_price('asset.eth', message_eth)
        
        time.sleep(10)


except KeyboardInterrupt:
    print("Publicador interrompido pelo usuário.")
finally:
    connection.close()
