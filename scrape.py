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
YOUTUBE_LINK = os.getenv('YOUTUBE_LINK')
EMAIL = os.getenv('EMAIL')

