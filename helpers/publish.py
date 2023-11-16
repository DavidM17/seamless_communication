import pika
import json

def add(body):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='host.docker.internal', 
        port=5672,
        #credentials=credentials
    ))
    except pika.exceptions.AMQPConnectionError as exc:
        print("Failed to connect to RabbitMQ service. Message wont be sent.")
        return

    cmd = json.dumps(body).encode('utf-8')

    channel = connection.channel()
    channel.queue_declare(queue='model_result')
    channel.basic_publish(
        exchange='',
        routing_key='model_result',
        body=cmd,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))

    connection.close()
    return