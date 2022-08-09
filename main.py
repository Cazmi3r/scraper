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

#------------------Variables------------------#
url_vividseat = 'https://www.vividseats.com/itzy-tickets-rosemont-rosemont-theatre-11-7-2022--concerts-k-pop/production/4000042?AID=Performer-MainProductionList'
file_vividseat = "vividseat.html"
excel_headers = ["price", "section type", "section number", "Row", "tickets avaliable"]
delay = 3000 
target_time = 3
load_dotenv()
email = environ.get("SCRAPE_RECEVING_EMAIL")
#---------------------------------------------#
while True:
    current_time = datetime.now()
    print(f"current time: {current_time}")
    # if current_time.hour == target_time:
    if True:    
        #############scrape vividseat data
        sm.scrape(url_vividseat, file_vividseat)
        
        ##############Update Vividseat excel
        df_vividseat = sm.dump_vividseats(file_vividseat, excel_headers)
        
        # "ï¿½" appears in the data where "-" should be this fixes that.
        df_vividseat["tickets avaliable"] = df_vividseat["tickets avaliable"].replace("ï¿½", "-", regex=True)
        
        
        df_vividseat.to_excel("vividseat.xlsx", index=False)

        #############Create The Email
        # Setup nylas api connection
        nylas = APIClient(
                        client_id=environ.get("NYLAS_CLIENT_ID"),
                        client_secret=environ.get("NYLAS_CLIENT_SECRET"),
                        access_token=environ.get("NYLAS_ACCESS_TOKEN")
                        )
        # Create your attachment
        attachment = open("vividseat.xlsx", "rb")
        attach = nylas.files.create()
        attach.filename = 'vividseat.xlsx'
        attach.stream = attachment
        
        # Draft your email and attach your file
        draft = nylas.drafts.create()
        draft.subject = "Ticket price update!"
        draft.body = "Hi Baby! heres your ticket prices for the day! They currently reflect the prices seen at Vividseat. Let me know how I can improve this!"
        draft.to = [{"name": "Mai Baby <3", "email": email}]
        draft.attach(attach)
        
        # Send your email!
        draft.send()
        attachment.close()
        
        print("Xlsx Sent")
    else:
        print(f"Target time of {target_time} not met")
    time.sleep(delay)