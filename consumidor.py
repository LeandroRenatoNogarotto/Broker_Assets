import pika
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

# Carregar a chave pública do publicador
with open("public_key.pem", "rb") as key_file:
    public_key = serialization.load_pem_public_key(key_file.read())

# Função para verificar a assinatura
def verify_signature(message, signature):
    try:
        public_key.verify(
            signature,
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

# Configuração do RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Função de callback para processar mensagens
def callback(ch, method, properties, body):
    # Dividir a mensagem e a assinatura
    message, signature = body.split(b'|', 1)
    try:
        # Decodificar a mensagem como UTF-8
        message_text = message.decode('utf-8')
        if verify_signature(message_text, signature):
            print(f"Mensagem verificada: {message_text}")
        else:
            print("Assinatura inválida.")
    except UnicodeDecodeError:
        print("Erro ao decodificar a mensagem.")

# Registrar interesse no tópico específico para BTC
channel.queue_declare(queue='btc_price')
channel.queue_bind(exchange='assets', queue='btc_price', routing_key='asset.btc')
channel.basic_consume(queue='btc_price', on_message_callback=callback, auto_ack=True)

print("Aguardando mensagens para BTC...")
channel.start_consuming()
