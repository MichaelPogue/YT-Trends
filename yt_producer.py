""" Modules
----------------------------------------------------------------------------"""
import os
import pandas as pd
import requests
import json
import pika
import sys
import webbrowser
import time
import csv
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from collections import deque
from time import strftime 
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
# URL = os.getenv('YOUTUBE_LINK')
URL = 'https://www.youtube.com/gaming/games'
EMAIL = os.getenv('EMAIL')
FILE_NAME = 'streamstatistics'

host = 'localhost'
queue = 'yt_streamstatistics'

response = requests.get(URL).text
soup = BeautifulSoup(response, 'html.parser')
primary_data = soup.body.find_all('script')[13].contents[0]

class ytData:
    """ 
    ----------------------------------------------------------------------------"""
    def __init__(self, primary_data) -> None:
        self.primary_data = primary_data
    
    def collect_data(self):
        data_name = []
        data_views = []

        """ 
        ----------------------------------------------------------------------------"""
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
        all_data.to_csv(f'{FILE_NAME}.csv')

        # return all_data

class ytSend:
    """ Step 2: Data Producer
    ----------------------------------------------------------------------------"""
    def rabbitmq_admin_site_offer():
        """Offer to open the RabbitMQ Admin website"""
        answer = input("Would you like to monitor RabbitMQ queues? y or n ")
        if answer.lower() == "y":
            webbrowser.open_new("http://localhost:15672/#/queues")
            print()

    """ 
    ----------------------------------------------------------------------------"""
    def queue_delete(host: str, queue: str):
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        ch = conn.channel()
        ch.queue_delete(queue)

    """ 
    ----------------------------------------------------------------------------"""
    def read_csv():
        csv_file = open(f'{FILE_NAME}.csv', 'r', encoding = 'utf-8')
        reader = csv.reader(csv_file, delimiter=",")
        next(reader)

        for row in reader:
            game_name = row[1]
            game_views = row[2]
            try:
                row_text = f"[{game_name}, {game_views}]"
                message = row_text.encode()
                ytSend.send_message(host, queue, message)
            except ValueError:
                pass

    """ 
    ----------------------------------------------------------------------------"""
    def send_message(host: str, queue: str, message):
        try:
            conn = pika.BlockingConnection(pika.ConnectionParameters(host))
            ch = conn.channel()
            ch.queue_declare(queue = queue, durable = True)
            ch.basic_publish(exchange = '', routing_key = queue, body = message)
            print(f"Message Sent: {message}")
            time.sleep(1)
        except pika.exceptions.AMQPConnectionError as e:
            print(f"ERROR! Connection to RabbitMQ server failed: {e}")
            sys.exit(1)
        finally:
            conn.close()

""" 
----------------------------------------------------------------------------"""
def main():
    yts = ytSend
    ytd = ytData
    ytd.collect_data(primary_data)
    yts.queue_delete(host, queue)
    # rabbitmq_admin_site_offer()
    yts.read_csv()

""" 
----------------------------------------------------------------------------"""
if __name__ == "__main__":
    main()