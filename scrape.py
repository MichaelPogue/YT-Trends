""" 
Step 1: Data Generation
-------------------------------------------------------------------------------
"""

import os
import pandas as pd
import requests
import json
import pika
import sys
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from collections import deque
from time import strftime 

# Set API parameters. 
load_dotenv()
# URL = os.getenv('YOUTUBE_LINK')
URL = 'https://www.youtube.com/gaming/games'
EMAIL = os.getenv('EMAIL')

host = 'localhost'
rmq_queue = "01-smoker"
rmq_deque = deque(maxlen = 5)
rmq_limit = 0 #######################


response = requests.get(URL).text
soup = BeautifulSoup(response, 'html.parser')
primary_data = soup.body.find_all('script')[13].contents[0]

data_name = []
data_views = []

try: 
    game_data = (
            json.loads(primary_data[20:-1])
            ['contents']
            ['twoColumnBrowseResultsRenderer']
            ['tabs'][0]
            ['tabRenderer']
            ['content']
            ['sectionListRenderer']
            ['contents'][0]
            ['itemSectionRenderer']
            ['contents'][0]
            ['shelfRenderer']
            ['content']
            ['gridRenderer']
            ['items']
        )

    for game in game_data:
        details = (
            game
            ['gameCardRenderer']
            ['game']
            ['gameDetailsRenderer']
        )

        game_data_name = details['title']['simpleText']
        game_data_views = details['liveViewersText']['runs'][0]['text']

        data_name.append(game_data_name)
        data_views.append(game_data_views)
except Exception:
    pass

name = pd.DataFrame(data_name, columns = [
    'name'])
views = pd.DataFrame(data_views, columns = [
    'views'])

all_data = name.join(views)

all_data.to_csv('streamstatistics.csv')

""" 
Step 2: Data Producer
-------------------------------------------------------------------------------
"""

""" Clear Queue
-----------------------------------------------------------------------------"""
def queue_delete(host: str, queue: str):
    # Connect to RabbitMQ.
    conn = pika.BlockingConnection(pika.ConnectionParameters(host))
    # Set channel.
    ch = conn.channel()
    # Clear the queues from the given variable.
    ch.queue_delete(queue)

""" Message Processing
-----------------------------------------------------------------------------"""
def read_csv():
    # Declared Variables.
    host = "localhost"
    queue_1 = "01-smoker"
    queue_2 = "02-food-A"
    queue_3 = "03-food-B"

    # CSV File Setup.
    # Set csv file to be used.
    csv_file = open("smoker-temps.csv", "r")
    # Create reader with a comma delimiter.
    reader = csv.reader(csv_file, delimiter=",")
    # Skip header in the dataset.
    next(reader)

    # Clear Queue
    # Clear individual queues to ensure queue is empty.
    queue_delete(host, queue_1)
    queue_delete(host, queue_2)
    queue_delete(host, queue_3)

    # Read Line by Line in a CSV Document
    for row in reader:
        # Set "id" as the times which all smokers have in common.
        smoker_time_id = row[0]

        # 01-smoker Queue Reader.
        try:
            # Set the next row in line to column 1.
            c1_row_text = float(row[1])
            # Configure row text to be sent as a message.
            row_text = f"[{smoker_time_id}, {c1_row_text}]"
            # Encode message for sending.
            message = row_text.encode()
            # Send data to RabbitMQ via the send_message function.
            send_message(host, queue_1, message)
            # Error dump. 
        except ValueError:
            pass

        # 02-food-A Queue Reader.
        try:
            # Set the next row in line to column 2.
            c2_row_text = float(row[2])
            # Configure row text to be sent as a message.
            row_text = f"[{smoker_time_id}, {c2_row_text}]"
            # Encode message for sending.
            message = row_text.encode()
            # Send data to RabbitMQ via the send_message function.
            send_message(host, queue_2, message)
            # Error dump. 
        except ValueError:
            pass

        # 03-food-B Queue Reader.
        try:
            # Set the next row in line to column 3.
            c3_row_text = float(row[3])
            # Configure row text to be sent as a message.
            row_text = f"[{smoker_time_id}, {c3_row_text}]"
            # Encode message for sending.
            message = row_text.encode()
            # Send data to RabbitMQ via the send_message function.
            send_message(host, queue_3, message)
            # Error dump. 
        except ValueError:
            pass

""" Send Message to RabbitMQ Servers
-----------------------------------------------------------------------------"""
def send_message(host: str, queue_name: str, message):
    try:
        # create a blocking connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        # use the connection to create a communication channel
        ch = conn.channel()
        # use the channel to declare a durable queue
        # a durable queue will survive a RabbitMQ server restart
        # and help ensure messages are processed in order
        # messages will not be deleted until the consumer acknowledges
        ch.queue_declare(queue=queue_name, durable=True)
        # use the channel to publish a message to the queue
        # every message passes through an exchange
        ch.basic_publish(exchange="", routing_key=queue_name, body=message)
        # print a message to the console for the user
        print(f" [x] Sent {message} from {queue_name}")
        time.sleep(.1)
    except pika.exceptions.AMQPConnectionError as e:
        print(f"ERROR! Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
        # close the connection to the server
        conn.close()

""" Code Command Center
-----------------------------------------------------------------------------"""
def main():
    # # Ask to launch website for monitoring. 
    # a = input("Open RabbitMQ monitoring website? (y or n)")
    # if a == "y":
    #     webbrowser.open_new("http://localhost:15672/#/queues")
    # else:
    #     pass
    # Begin task of sending message.
    read_csv()

"""  
Launch Code!
------------------------------------------------------------------------------------------ """
# Standard Python idiom to indicate main program entry point
# This allows us to import this module and use its functions
# without executing the code below.
# If this is the program being run, then execute the code below
if __name__ == "__main__":
    main()