import pika
from helpers import transform

def listen():
    # credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost', 
        port=5672,
        #credentials=credentials
    ))
    channel = connection.channel()

    channel.queue_declare(queue='audio_uploaded')

    channel.basic_consume(queue='audio_uploaded', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages')
    channel.start_consuming()

def callback(ch, method, properties, body):
    transform.evaluate(body)
    
try:
    listen()
except:
    print("Failed to connect to RabbitMQ service")