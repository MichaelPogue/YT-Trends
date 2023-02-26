import pika
import sys
import time
import os
from collections import deque
from time import strftime 
from dotenv import load_dotenv

host = 'localhost'
queue = 'yt_streamstatistics'
data_deque = deque(maxlen = 5)
data_warning = 16000

load_dotenv()
EMAIL = os.getenv("EMAIL_ADDRESS")

def decode_message(ch, method, properties, body):
    """  """
    print(f"Received:      {body.decode()} at {strftime('%H:%M:%S')}")
    data_deque.append(body.decode())
    initial_data = body.decode()
    initial_split = initial_data.split(",")
    data = initial_split[1][:-1]

    if character_detection(data, '.') == True:
        remove_period = data.replace('.', '')
        remove_letter = remove_period.replace('K','')
        data_final = int(remove_letter)*100
        # print(f'--------------> {data_final}')
    elif character_detection(data, '.') == False:
        remove_letter = data.replace('K','')
        data_final = int(remove_letter)*1000
        # print(f'--------------> {data_final}')

    if data_final >= data_warning:
        print("Received:      ")
        print("--------------> BIG NUMBER")
    elif data_final < data_warning:
        pass

    ch.basic_ack(delivery_tag = method.delivery_tag)
    time.sleep(1)

def character_detection(string, chars):
    for char in string:
        if char in chars:
            return True
    return False

def main(hn: str, qn: str):
    """  """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host = hn))
    except Exception as e:
        print("ERROR: connection to RabbitMQ server failed.")
        print(f"Verify the server is running on host={hn}.")
        print(f"The error says: {e}")
        sys.exit(1)
    try:
        channel = connection.channel()
        channel.queue_declare(queue = qn, durable = True)
        channel.basic_qos(prefetch_count=1) 
        channel.basic_consume( queue = qn, on_message_callback = decode_message)
        print("Ready for work. To exit press CTRL+C.")
        channel.start_consuming()
    except Exception as e:
        print("ERROR: Something went wrong.")
        print(f"The error says: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nUser interrupted continuous listening process.")
        sys.exit(0)
    finally:
        print("\nClosing connection. Goodbye.\n")
        connection.close()

"""  """
if __name__ == "__main__":
    main(host, queue)