Elabore um documento que descreva a importância de uma arquitetura orientada a eventos na comunicação indireta entre quatro sistemas e implemente essa comunicação na linguagem desejada. 

Dois desses sistemas são clientes publicadores e vão gerar eventos (mensagens). Esse cliente publicador deve assinar digitalmente cada mensagem publicada com a sua chave privada. 

Dois sistemas são clientes consumidores ou assinantes e vão registrar interesse em receber notificações de eventos. Esse cliente consumidor precisa verificar a assinatura da mensagem usando a chave pública correspondente.

Utilizem o serviço de mensageria (message broker) RabbitMQ e o protocolo AMQP (Advanced Message Queuing Protocol) para permitir a comunicação indireta entre os processos clientes. O broker é responsável por enviar notificações de eventos aos clientes assinantes interessados.

Tutorial de clientes RabbitMQ disponível para várias linguagens:
