import os
import re
import json
import sys
import time
from dotenv import load_dotenv, find_dotenv
from datetime import datetime

from selenium import webdriver  
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.common.keys import Keys

from twilio.rest import Client
TWILIO_NUMBER = "+12155932275"
testMode = False

def log(message):
	date_format = "%d-%m-%Y %H:%M:%S"
	timestamp = "[" + datetime.now().strftime(date_format) + "] "
	with open("log.log", "a+") as f:
		message = timestamp + message + "\n"
		f.write(message)
		f.close()		

def getWebsite():
    print("Pulling site")
    log("Pulling site")

    chrome_options = Options()  
    chrome_options.add_argument("--headless")
    # chrome_options.binary_location = os.environ['GOOGLE_CHROME_BIN']
    chrome_driver = os.environ['CHROMEDRIVER_PATH']
    driver = webdriver.Chrome(chrome_driver, options=chrome_options)
    driver.implicitly_wait(5)
    driver.get("https://app.smartsheet.com/b/publish?EQBCT=1fb10103a37c4383b3e11b5e50c5a50d")

    dedupedElements = list(set([x.text for x in driver.find_elements_by_class_name("gridCellContent")]))
    return (dedupedElements)

def checkDates(possibleElements):
    print("Checking dates")
    log("Checking Dates");

    # Import "database" of already-seen dates
    seenDates = json.load(open('seen_dates.json', 'r'))["dates"]

    for date in possibleElements:
        # Find date entries in the cell contents
        if re.search("\d{1,2}/\d{1,2}", date) is not None:
            if date not in seenDates:
                sendText(date)

                # Update the "database"
                if (not testMode):
                    seenDates.append(date)
                    with open('seen_dates.json', 'w') as json_file:
                        json.dump({"dates": seenDates}, json_file)

def sendText(date):
    print("Sending for {0}".format(date))
    log("Sending for {0}".format(date))

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)
    amy_phone = os.environ['AMY_PHONE']

    message = client.messages \
        .create(
                body = "New lab slots for {0}".format(date),
                from_=TWILIO_NUMBER,
                to=amy_phone
            )

def run():
    load_dotenv(find_dotenv())
    checkDates(getWebsite())

if (len(sys.argv) > 1):
	if ("-t" in sys.argv):
		testMode = True
run()
