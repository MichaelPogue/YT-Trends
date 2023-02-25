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

load_dotenv()
# URL = os.getenv('YOUTUBE_LINK')
URL = 'https://www.youtube.com/gaming/games'
EMAIL = os.getenv('EMAIL')
FILE_NAME = 'streamstatistics'

rmq_host = 'localhost'
rmq_queue = 'yt_streamstatistics'
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

def rabbitmq_admin_site_offer():
    """Offer to open the RabbitMQ Admin website"""
    answer = input("Would you like to monitor RabbitMQ queues? y or n ")
    if answer.lower() == "y":
        webbrowser.open_new("http://localhost:15672/#/queues")
        print()

""" Clear Queue
-----------------------------------------------------------------------------"""
def queue_delete(host: str, queue: str):
    conn = pika.BlockingConnection(pika.ConnectionParameters(host))
    ch = conn.channel()
    ch.queue_delete(queue)

""" Message Processing
-----------------------------------------------------------------------------"""
def read_csv():
    csv_file = open(f'{FILE_NAME}.csv', "r")
    reader = csv.reader(csv_file, delimiter=",")
    next(reader)

    for row in reader:
        smoker_time_id = row[0]
        try:
            c1_row_text = float(row[1])
            row_text = f"[{smoker_time_id}, {c1_row_text}]"
            message = row_text.encode()
            send_message(rmq_host, rmq_queue, message)
        except ValueError:
            pass

""" Send Message to RabbitMQ Servers
-----------------------------------------------------------------------------"""
def send_message(host: str, queue_name: str, message):
    try:
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        ch = conn.channel()
        ch.queue_declare(queue=queue_name, durable=True)
        ch.basic_publish(exchange="", routing_key=queue_name, body=message)
        print(f" [x] Sent {message} from {queue_name}")
        time.sleep(.1)
    except pika.exceptions.AMQPConnectionError as e:
        print(f"ERROR! Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
        conn.close()

""" Code Command Center
-----------------------------------------------------------------------------"""
def main():
    queue_delete(rmq_host, rmq_queue)
    # rabbitmq_admin_site_offer()
    read_csv()

"""  
Launch Code!
------------------------------------------------------------------------------------------ """
if __name__ == "__main__":
    main()