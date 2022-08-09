from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import time

# goal of this class is to be able to scrape a site, parse it for a data set
# and export that data set
# maybe a ScrapeManager object should keep track of all of the data sets it has parsed
# this way I could easily scrape and parse many sites quickly then compile them in some way
# maybe it should be able to combine multiple data sets to create one output
class ScrapeManager:
#------------------Methods------------------#
    def scrape(self, url, file):
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
    def load_soup_from_file(self, file):
        html = open(file, "r").read()
        return BeautifulSoup(html, features="html.parser")

    # get list of divs to parse
    def get_divs(self, soup):
        all_divs = soup.find_all("div", "styles_listingRowContainer__3hXZy")
        dirty_data = []
        for div in all_divs:
            words = div.text.split()
            dirty_data.append(words)
        return dirty_data

    # Get data dump from vividseats
    # TODO Make this Method Generic
    def dump_vividseats(self, save_file, excel_headers):
        # load HTML into Beautiful soup
        soup = self.load_soup_from_file(save_file)
        
        # clean data that will be returned at the end
        df_clean_data = pd.DataFrame(columns=excel_headers)
        
        # find the Divs with the pricing info and build rows for a panda data frame
        all_divs = self.get_divs(soup)  
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