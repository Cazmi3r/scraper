from turtle import delay
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
from nylas import APIClient
import time
from datetime import datetime
from dotenv import load_dotenv
from os import environ
import ScrapeManager as sm

# the goal of this class is to create a collection of parsing alagorithms
# that can be passed to the a Scrape Manager object to seperate parsing logic
class Parsers:
    def test(self):
        pass