from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import pika
import threading
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

app = Flask(__name__)
socketio = SocketIO(app)

# Carregar as chaves públicas dos publicadores
with open("public_key.pem", "rb") as key_file1:
    public_key1 = serialization.load_pem_public_key(key_file1.read())

with open("public_key2.pem", "rb") as key_file2:
    public_key2 = serialization.load_pem_public_key(key_file2.read())


# Função para verificar a assinatura da mensagem
def verify_signature(message, signature, public_key):
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


# Função para escutar preços no RabbitMQ
def rabbitmq_listener(selected_assets):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='assets', exchange_type='topic')

    queues = {}
    for asset in selected_assets:
        queue_name = f"{asset}_price_queue"
        channel.queue_declare(queue=queue_name)
        channel.queue_bind(exchange='assets', queue=queue_name, routing_key=f'asset.{asset}')
        queues[asset] = queue_name

    # No código do consumidor (RabbitMQ listener callback):
    def callback(ch, method, properties, body):
        message, signature = body.split(b'|', 1)
        price = message.decode('utf-8')  # Somente o valor numérico

        # Selecionar a chave pública apropriada
        if 'Compra' in price:
            public_key = public_key2
        else:
            public_key = public_key1

        if verify_signature(price, signature, public_key):
            asset = method.routing_key.split('.')[1]
            formatted_message = f" {asset.upper()}: $ {price}"  # Formatação única e clara
            socketio.emit('price_update', {'asset': asset, 'price': formatted_message})


    for queue in queues.values():
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('subscribe')
def handle_subscription(data):
    selected_assets = data['assets']
    thread = threading.Thread(target=rabbitmq_listener, args=(selected_assets,))
    thread.start()
    emit('subscription_status', {'status': 'subscribed', 'assets': selected_assets})


@socketio.on('buy')
def handle_buy(data):
    asset = data['asset']
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='assets', exchange_type='topic')
    buy_message = f"Compra solicitada para {asset}"

    # Publicar a solicitação de compra no RabbitMQ
    channel.basic_publish(exchange='assets', routing_key=f'buy.{asset}', body=buy_message.encode())
    connection.close()

    emit('purchase_status', {'status': 'compra realizada', 'asset': asset})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)
