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

except Exception:
    pass

# class ytTrends:
#     def __init__(self, URL, EMAIL):
#         self.URL = URL
#         self.EMAIL = EMAIL

#     def get_website_data(self):
#         response = requests.get(URL).text
#         soup = BeautifulSoup(response, 'html.parser')

# ytt = ytTrends