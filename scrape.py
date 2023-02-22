""" 

-------------------------------------------------------------------------------
"""

import os, csv, schedule, datetime, time
import pandas as pd
from googleapiclient.discovery import build

from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

# Set global variable parameters. 
load_dotenv()
# YOUTUBE_LINK = os.getenv('YOUTUBE_LINK')
YOUTUBE_LINK = 'https://www.youtube.com/gaming/games'
EMAIL = os.getenv('EMAIL')
WEBSITE_TEXT = requests.get(YOUTUBE_LINK).text
SOUP = BeautifulSoup(WEBSITE_TEXT, 'lxml')