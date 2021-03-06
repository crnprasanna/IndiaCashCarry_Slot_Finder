#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
    User configuation module
	
Linux path - You can find by running command:
>>which chromedriver
CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'

Windows path - Downloaded absolute path
CHROME_DRIVER_PATH = '<PATH_TO_CHROMEDRIVER_win32>\\chromedriver.exe'


Supported India cash and carry stores list:
1. Sunnyvale
2. San Jose
3. Fremont

'''

CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'

ICC_LOGIN_EMAIL = '<YOUR_IndiaCashCarry_LOGIN_ID>'
ICC_LOGIN_PASS = '<YOUR_IndiaCashCarry_PASSWORD>'

# Option : 'ALL' will find slots in all 3 stores
# To find specific stores, Enter one from list - [ 'Sunnyvale', 'San Jose', 'Fremont' ]
# Example : ICC_STORES_TO_CHECK = "ALL"
# Example : ICC_STORES_TO_CHECK = "San Jose"

ICC_STORES_TO_CHECK = "All"

# 'Delivery' or 'Pickup' or 'Both'
# Both -> Will check Delivery or Pickup and email if any one status is found
# Delivery -> Only if Delivery slot available, it will send email

ICC_STATUS_TO_CHECK = "Both" 


SEND_EMAIL = True

# Needs below information, if you set SEND_EMAIL flag True
# Check readme for more information

SENDER_GMAIL_ID =  '<YOUR_GMAIL_LOGIN_ID>'  # ex: test@gmail.com
SENDER_GMAIL_PASS = '<YOUR_GMAIL_PASSWORD>'  # Gmail app specific passwords or gmail login password
RECEIVER_EMAIL_ID = '<RECEIVER_EMAIL_ID>'  # Ex: test@hotmail.com
