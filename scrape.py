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

url_text = requests.get(URL).text
soup = BeautifulSoup(url_text, 'html.parser')

elem = soup.find_all('div')
print(elem)