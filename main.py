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





#------------------Variables------------------#
url_vividseat = 'https://www.vividseats.com/itzy-tickets-rosemont-rosemont-theatre-11-7-2022--concerts-k-pop/production/4000042?AID=Performer-MainProductionList'
file_vividseat = "vividseat.html"
excel_headers = ["price", "section type", "section number", "Row", "tickets avaliable"]
delay = 3000 
target_time = 3
current_time = datetime.now()
email = environ.get("SCRAPE_RECEVING_EMAIL")
load_dotenv()
#------------------Methods------------------#
def scrape(url, file):
    # setup the options for our webDriver
    options = Options()
    options.headless = False
    options.add_argument("--window-size=1920,1200")

    # installs and runs the Chrome Driver
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
    driver.get(url)
    time.sleep(10)
    html = driver.page_source
    driver.quit()   
    
    # saves the scrapped HTML to my save file
     
    save_file = open(file, "w")
    save_file.write(html)

# loads HTML from file into BeautifulSoup 
def load_soup(file):
    html = open(file, "r").read()
    return BeautifulSoup(html, features="html.parser")

# get list of divs to parse
def get_divs(soup):
    all_divs = soup.find_all("div", "styles_listingRowContainer__3hXZy")
    dirty_data = []
    for div in all_divs:
        words = div.text.split()
        dirty_data.append(words)
    return dirty_data

# Get data dump from vividseats
def dump_vividseats(save_file, excel_headers):
    # load HTML into Beautiful soup
    soup = load_soup(save_file)
    
    # clean data that will be returned at the end
    df_clean_data = pd.DataFrame(columns=excel_headers)
    
    # find the Divs with the pricing info and build rows for a panda data frame
    all_divs = get_divs(soup)  
    for div in all_divs:
        output = {}
        output["price"] = div[0]
        output["section type"] = div[1][2:]
        output["section number"] = div[2]
        
        # the row and ticket data were mixed into one field when importing
        # this was the solution
        row_tickets = div[5]
        
            # what happens when string starts with a letter
            # this happens when the seat is not a pit seat
        if re.search("^[a-zA-Z]", row_tickets) is not None:
            
            # loop over row and ticket avaliable data to find first number
            # then set the row and tickets avaliable values
            # TODO FIX THIS SHIT and add logs
            i = 0
            for current_char in row_tickets:
                if current_char.isnumeric():
                    output["Row"] = row_tickets[0:i]
                    output["tickets avaliable"] = row_tickets[i:]
                    break
                i = i + 1
                
            # what happens when string starts with a number
        else:
            output["Row"] = row_tickets[0:1]
            output["tickets avaliable"] = row_tickets[1:]
        
        df_to_append = pd.DataFrame(output, index=[0])
        df_clean_data = pd.concat([df_clean_data, df_to_append])  
    return df_clean_data

#------------------Project Logic------------------#
while True:
    if current_time.hour == target_time:
        #############scrape vividseat data
        scrape(url_vividseat, file_vividseat)
        #############
        
        ##############Update Vividseat excel
        df_vividseat = dump_vividseats(file_vividseat, excel_headers)
        
        # "ï¿½" appears in the data where "-" should be this fixes that.
        df_vividseat["tickets avaliable"] = df_vividseat["tickets avaliable"].replace("ï¿½", "-", regex=True)
        
        df_vividseat.to_excel("vividseat.xlsx", index=False)
        ##############

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
        print("Target time not met")
    time.sleep(delay)