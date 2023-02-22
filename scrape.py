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
# YOUTUBE_LINK = os.getenv('YOUTUBE_LINK')
YOUTUBE_LINK = 'https://www.youtube.com/gaming/games'
EMAIL = os.getenv('EMAIL')

