""" 
Authored By: Michael Pogue | Created on: 22Feb23 | Last Updated: 25Feb23 

"""

import pika
import sys
import time
import os
from collections import deque
from time import strftime 
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv("EMAIL_ADDRESS")
FILE_NAME = 'streamstatistics'

host = 'localhost'
queue = 'yt_streamstatistics'
data_deque = deque(maxlen = 5)
data_warning = 100000

def callback(ch, method, properties, body):
    print(f"Received: {body.decode()} at {strftime('%H:%M:%S')}")
    time.sleep(body.count(b"."))
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main(hn: str, qn: str):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hn))


    except Exception as e:
        print("\nERROR: connection to RabbitMQ server failed.")
        print(f"Verify the server is running on host = {hn}.")
        print(f"Error Message: {e}.")
        sys.exit(1)

    try:
        channel = connection.channel()
        channel.queue_declare(queue=qn, durable=True)
        channel.basic_qos(prefetch_count=1) 
        channel.basic_consume( queue=qn, on_message_callback=callback)
        print("Listening, press CTRL+C to exit.")
        channel.start_consuming()


    except Exception as e:
        print("\nERROR: Something went wrong.")
        print(f"The error says: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nUser interrupted continuous listening process.")
        sys.exit(0)
    finally:
        print("\nConnection terminated.")
        connection.close()

if __name__ == "__main__":
    host = 'localhost'
    queue = "yt_streamstatistics"
    main(host, queue)
