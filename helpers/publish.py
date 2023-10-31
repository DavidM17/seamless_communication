import pika
import json

def add(cmd):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    except pika.exceptions.AMQPConnectionError as exc:
        print("Failed to connect to RabbitMQ service. Message wont be sent.")
        return
    
    cmd_obj = json.loads(cmd.decode("utf-8").replace("'",'"'))
    cmd_obj['Date']  = '383994'

    cmd = json.dumps(cmd_obj).encode('utf-8')

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