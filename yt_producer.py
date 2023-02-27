""" 
Developed By: Michael Pogue
Created:      2023.02.22
Last Updated: 2023.02.27

Note:
This code represents a two-part system, yt_producer.py and yt_consumer.py. 

Purpose:
The purpose for this segment is to use BeautifulSoup to read and parse the
data from YouTube's list of currently streamed video games. It reads the
JSON data from YouTube and converts that data into names and view counts.
Finally, the data is written to a CSV file and streamed to RabbitMQ's 
servers; which will later be read by yt_consumer.py.
----------------------------------------------------------------------------"""

# Load necessary modules for code.
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

# Set up environment. 
load_dotenv()
URL = os.getenv('YOUTUBE_LINK')
# URL = 'https://www.youtube.com/gaming/games'

# Set default variables.
FILE_NAME = 'streamstatistics'
host = 'localhost'
queue = 'yt_streamstatistics'

# Use BeautifulSoup module to parse requested URL.
response = requests.get(URL).text
soup = BeautifulSoup(response, 'html.parser')
primary_data = soup.body.find_all('script')[13].contents[0]

class ytData:
    """ Class that contains primary data scrape methods.
    ------------------------------------------------------------------------"""
    def __init__(self, primary_data) -> None:
        self.primary_data = primary_data

    def collect_data(self):
        """ Method to scrape data from Youtube URL.
        --------------------------------------------------------------------"""        
        data_name = []
        data_views = []

        # Sort JSON data into an array only for names and views.
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

        # Insert data into a single DataFrame.
        name = pd.DataFrame(data_name, columns = [
            'name'])
        views = pd.DataFrame(data_views, columns = [
            'views'])
        all_data = name.join(views)
        all_data.to_csv(f'{FILE_NAME}.csv')

class ytSend:
    """ Class to clear queues, read CSV file, & send the message to RabbitMQ.
    ------------------------------------------------------------------------"""
    def rabbitmq_admin_site_offer():
        """ Method asking to off to monitor RabbitMQ primary servers.
        --------------------------------------------------------------------"""       
        answer = input("Would you like to monitor RabbitMQ queues? y or n ")
        if answer.lower() == "y":
            print("Username: guest.")
            print("Password: guest.")
            webbrowser.open_new("http://localhost:15672/#/queues\n")

    def queue_delete(host: str, queue: str):
        """ Method to clear any queues already pending.
        --------------------------------------------------------------------""" 
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        ch = conn.channel()
        ch.queue_delete(queue)

    def read_csv():
        """ Method to read CSV file already generated.
        --------------------------------------------------------------------""" 
        csv_file = open(f'{FILE_NAME}.csv', 'r', encoding = 'utf-8')
        reader = csv.reader(csv_file, delimiter=",")
        next(reader)
        # Read CSV data row by row, then send to RabbitMQ.
        for row in reader:
            game_name = row[1]
            game_views = row[2]
            try:
                row_text = f"[{game_name}, {game_views}]"
                message = row_text.encode()
                ytSend.send_message(host, queue, message)
            except ValueError:
                pass

    def send_message(host: str, queue: str, message):
        """ Method to send data obtained through read_csv to RabbitMQ.
        --------------------------------------------------------------------""" 
        try:
            conn = pika.BlockingConnection(pika.ConnectionParameters(host))
            ch = conn.channel()
            ch.queue_declare(queue = queue, durable = True)
            ch.basic_publish(exchange = '', routing_key = queue, body = message)
            print(f"Message Sent: {message}")
            time.sleep(1)
        except pika.exceptions.AMQPConnectionError as e:
            print(f"ERROR! Connection to RabbitMQ server has failed. Error: \n{e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nUser interrupted continuous listening process.\n")
            sys.exit(0)
        finally:
            conn.close()

def main():
    """ Main function to setup and launch individual components of code.
    ------------------------------------------------------------------------"""
    ytd = ytData
    yts = ytSend
    ytd.collect_data(primary_data)
    yts.queue_delete(host, queue)
    yts.rabbitmq_admin_site_offer()
    yts.read_csv()

if __name__ == "__main__":
    """ Primary function to launch code.
    ------------------------------------------------------------------------"""
    main()