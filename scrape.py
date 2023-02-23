""" 

-------------------------------------------------------------------------------
"""

import os, csv, schedule, datetime, time
import pandas as pd
from googleapiclient.discovery import build

from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

# Set API parameters. 
load_dotenv()
# URL = os.getenv('YOUTUBE_LINK')
URL = 'https://www.youtube.com/gaming/games'
EMAIL = os.getenv('EMAIL')

response = requests.get(URL).text
soup = BeautifulSoup(response, 'html.parser')

primary_data = soup.body.find_all('script')[13].contents[0]

# class ytTrends:
#     def __init__(self, URL, EMAIL):
#         self.URL = URL
#         self.EMAIL = EMAIL

#     def get_website_data(self):
#         response = requests.get(URL).text
#         soup = BeautifulSoup(response, 'html.parser')

# ytt = ytTrends