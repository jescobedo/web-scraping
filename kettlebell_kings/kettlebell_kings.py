import sys
import configparser
import time

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


config = configparser.ConfigParser()
config.read('kettlebell_kings.ini')
twilio_config = config['twilio']
sendgrid_config = config['sendgrid']

# Main URL
POWDER_COAT_KB_URL = 'https://www.kettlebellkings.com/powder-coat-kettlebell/'

# Map of product IDs to weights (in kg)
KB_MAP_GROUP_1 = {f'{2215 + i}': (4 + 2 * i) for i in range(11)}
KB_MAP_GROUP_2 = {f'{2226 + i}': (28 + 4 * i) for i in range(6)}
KB_MAP_GROUP_3 = {f'{4622 + i}': (56 + 12 * i) for i in range(4)}
KB_MAP = {**KB_MAP_GROUP_1, **KB_MAP_GROUP_2, **KB_MAP_GROUP_3}

# Kettlebell weights we want to monitor (in kg)
KB_TO_MONITOR = [24, 16, 32]

twilio_client = Client(twilio_config['sid'], twilio_config['token'])

def send_sms(text):
    try:
        twilio_client.messages.create(
            to=twilio_config['to'], 
            from_=twilio_config['from'], 
            body=text
        )
    except Exception as e:
        print(e.message)

def send_email(subject, body):
    message = Mail(
        from_email=sendgrid_config['from'],
        to_emails=sendgrid_config['to'],
        subject=subject,
        html_content=body)
    try:
        sg = SendGridAPIClient(sendgrid_config['api_key'])
        response = sg.send(message)
    except Exception as e:
        print(e.message)


if __name__ == '__main__':

    chrome_options = Options()
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(POWDER_COAT_KB_URL)

    try:
        select = Select(driver.find_element_by_id('attribute_select_886'))
    except NoSuchElementException:
        send_sms('Kettlebell Kings changed their KB form select ID!!!')
        sys.exit()

    # Get product IDs for KB of interest
    ids_to_monitor = [id_ for id_, weight in KB_MAP.items() if weight in KB_TO_MONITOR]

    # Loop through KB options and see if any KB of interest 
    # is in stock based on text in the dropdown menu
    ids_in_stock = []
    for kettlebell_option in select.options:
        kettlebell_id = kettlebell_option.get_attribute('value')
        kettlebell_name = kettlebell_option.text.lower()
        if (kettlebell_id not in ids_to_monitor) or ('out of stock' in kettlebell_name):
            continue

        # If we get to this point, we've found a KB we're interested in
        # that is apparently in stock. So, we'll select it and check if it
        # the division with id="instocknotify-container" shows up.
        # If it doesn't, the KB is in stock.
        select.select_by_value(kettlebell_id)

        # Sleep for a few seconds to see if the out of stock div shows up. 
        # Using this instead of the usual Wait objects provided by Selenium 
        # because the div is the exact same for all KB options: 
        # if it's already visible and we select another KB the only 
        # way to know if the div is present for the latter is to just wait
        # for it to load.
        time.sleep(10)
        try:
            in_stock_notify_div = driver.find_element_by_id('instocknotify-container')
        except NoSuchElementException:
            ids_in_stock.append(kettlebell_id)

    if ids_in_stock:
        kbs_in_stock = ', '.join([f'{KB_MAP[kb]} kg' for kb in ids_in_stock])
        message = f'The following KBs are now in stock! {kbs_in_stock}. Go to {POWDER_COAT_KB_URL}'
        send_sms(message)
        send_email('Kettlebell Kings just had a restock!', message)
    else:
        print('No KBs in stock')

    driver.quit()
