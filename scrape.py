""" 

-------------------------------------------------------------------------------
"""

import os, csv, schedule, datetime, time
import pandas as pd
import requests
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Set API parameters. 
load_dotenv()
# URL = os.getenv('YOUTUBE_LINK')
URL = 'https://www.youtube.com/gaming/games'
EMAIL = os.getenv('EMAIL')

response = requests.get(URL).text
soup = BeautifulSoup(response, 'html.parser')
primary_data = soup.body.find_all('script')[13].contents[0]

class ytGameTrends:
    def __init__(self, EMAIL):
        self.EMAIL = EMAIL
        self.primary_data = primary_data

    def get_data(self):
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

        return data_name, data_views

ytg = ytGameTrends
a, b = ytg.get_data(primary_data)

a