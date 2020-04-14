# India Cash and Carry Slot Finder

A Windows / Linux based python module to find India Cash and carry delivery/pickup slot finder. 

[India cash and carry](https://www.indiacashandcarry.com/) is the well known Indian grocery chain in SF Bay area 


# Inspirations:
Personally I was stuck with COVID-19 pandaemic at home for getting my day to day essentials and started looking online grocery delivery services. 

One challange with those platforms is finding slots in my area due to surge in demand for those services and it's nearly impossible for me to get a slot. When checking with my friends and colleagues, I found most of us have the same problem. 	

This tool was created to help people who are at high risk and those needy ones (including myself)
	
# Cloning repro

      git clone https://github.com/crnprasanna/IndiaCashCarry_Slot_Finder.git
      
      Note: Make sure you get latest changes running command "git pull" before running each time


# Installation:

1. Windows:

        a. Python : v3 and above and python pip3
        b. Latest google chrome and chromedriver corresponding to chrome version installed
	  
2. Ubuntu:
	
          sudo ./install_ubuntu.sh # under 'install/' directory
          **Note : This tool will auto upgrade chrome to latest version, if not installed on the host pc already
	
  
3. Installing python modules:

          pip3 install -r requirements.txt
		  

# Limitations:

1. Supports GMAIL based notifications only (If you don't wish to get gmail notification, you may still find status from logs)


# How to use the tool 

1. Configure the settings.py file

	a. ICC_STORES_TO_CHECK
  
		ICC_STORES_TO_CHECK = "All"  
		Option : 'ALL' will find slots in all 3 stores [ 'Sunnyvale', 'San Jose', 'Fremont' ]
    		
		Example : ICC_STORES_TO_CHECK = "ALL"    
		In above example, make sure you have added items in all stores manually before running the script
		
		Example : ICC_STORES_TO_CHECK = "San Jose"    
		Note : In above example, uou should have added items manually in "San Jose" store before running the script

	b. Provide your instacart login details. 
  
		ICC_LOGIN_EMAIL = "<your_icc_email_id>"
		ICC_LOGIN_PASS = "<your_icc_password>"
		
    
	c. ICC_STATUS_TO_CHECK = "Both"
  
		This option will check slots for - 'Delivery' or 'Pickup' or 'Both'		
		Both -> Will check Delivery or Pickup and email if any one status is found		
		Delivery -> Only if Delivery slot available, it will send email


	c. Receiving email notification:
	
		SEND_GMAIL = True  # Options : True or False
		
		Note: 
		
		a. If you set the option "SENG_GMAIL = False", 
			- you won't get email notifications 
			- you will get the status printed on console and in log file under 'logs/' directory
			- you can leave the below fields as is (SENDER_GMAIL_ID, SENDER_GMAIL_PASS, RECEIVER_EMAIL_ID
		
		SENDER_GMAIL_ID = "<YOUR_GMAIL_ID>"
		SENDER_GMAIL_PASS = "<YOUR_GMAIL_PASSWORD/App specific password>"
		RECEIVER_EMAIL_ID = "<EMAIL_ID_TO_RECIVE_NOTIFICATIONS>"
		
		b. If you have set the option "SENG_GMAIL = True",  
			 - You will get email notifications, provided have configured below details
			 - If you have enabled Two factor authentication in your gmail account, you can proivide App specific password generated, follow : https://support.google.com/accounts/answer/185833?hl=en
			 - If you haven't enabled 2FA, then you need to provide gmail password and need to turn on "allow less secure apps from your gmail id" 
				#Steps:
				#1. GOTO : https://myaccount.google.com/u/0/lesssecureapps?pageId=none
				#2. Turn on : "Allow less secure apps"



2. Executing the script:
		
		Note : Make sure you have updated settings.py
		
		> python3 ./icc_slot_finder.py
		

3. Stopping the script:

		Script will stop once the slot is found  
		If you want to stop execution, you can press 'ctrl + c'
		

4. Logs:
	
		Logs will be generated under logs/ folder. Also, logs will be printed on console
	
		
# Sample Output: 


    ##########################################
    (16:03:17) root | Input Config:
    (16:03:17) root | 	Chrome driver path: C:\Users\user\Downloads\chromedriver_win32\chromedriver.exe
    (16:03:17) root | 	Stores List: ALL
    (16:03:17) root | 	Pickup/Delivery: DELIVERY
    (16:03:17) root | 	ICC Login: xxxx@gmail.com
    (16:03:17) root | 	SEND_EMAIL report: True
    ##########################################
    (16:03:28) root | Attempting to login...
    (16:03:38) root | Login succeeded
    (16:03:38) root | Starting new loop
    (16:04:38) root | FREMONT Delivery Slot : False
    (16:04:38) root | SUNNYVALE Delivery Slot : True
    (16:04:38) root | SAN JOSE Delivery Slot : False
    (16:04:40) root | Email notification succesfully sent
    (16:04:42) root | Connection ended
    ##########################################


# Tested platforms:

	Tested on Windows 10 and Ubuntu 16.04
	

# Tested tool versions:
	Python3
	Google Chrome 81.0.4044.92
	Chromedriver v81.0.4044.92
	selenium v3.141.0		
	
# Known Issues:

	NA

	
# Disclaimer:

	No guarantee that you will get the slots as reported by tool, as the slot booking happens at realtime.
	
	Script may take longer time find slots as I don't have any control over India cash and carry slot availbality logic.

	This tools is for personnal-noncommercial use only.
