#C:\\Users\\prasannan\\AppData\\Local\\lxss\\home\\nvidia

#pip install selenium chromedriver
#pip install pyvirtualdisplay
#pip install xvfbwrapper

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
import time
from signal import signal, SIGINT
from sys import exit



class Browser():
	def __init__(self, driverpath, logger=None):

		self.driver = None
		self.driverpath = driverpath
		self.logger = logger
		self.supported_actions = [ 'clear', 'click', 'send_text', 'read_text' ]


	def printlog(self, msg):
		if self.logger:
			self.logger.log(msg)
		else:
			print(msg)

	
	def start(self, headless=True):
		self.printlog("Going to init browser")

		try:
			if headless:
				self.__init_browser__()
			else:
				self.__init_browser_head__()

			self.driver.set_page_load_timeout(30)
		except Exception as err:

			self.printlog("BROWSER CANT LAUNCH, err {}\n".format(err))
			self.close()
			raise Exception(err)

	
	def __init_browser__(self):
		options = webdriver.ChromeOptions();
		options.add_argument('--headless');
		options.add_argument('log-level=3')
		options.add_argument('window-size=1920,1080')
		options.add_argument('--no-sandbox')
		options.add_argument('--single-process')

		user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
		options.add_argument('user-agent={0}'.format(user_agent))


		capabilities = DesiredCapabilities.CHROME.copy()
		capabilities['acceptSslCerts'] = True
		capabilities['acceptInsecureCerts'] = True

		self.driver = webdriver.Chrome(executable_path=self.driverpath, chrome_options=options, desired_capabilities=capabilities)
		self.driver.delete_all_cookies()

	
	def __init_browser_head__(self):
		options = webdriver.ChromeOptions();
		options.add_argument('window-size=1920,1080')

		user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
		options.add_argument('user-agent={0}'.format(user_agent))


		self.driver = webdriver.Chrome(executable_path=self.driverpath, chrome_options=options)
		self.driver.delete_all_cookies()


	def load_url(self, url, delay=3):
		self.driver.get(url)
		time.sleep(delay) #time to launch webpage
		

	def screenshot(self, file="browser.png"):
		self.driver.save_screnshot(file)
		
	
	def perform_by_tagname(self, tagname, action, text=None, delay=2):
		if action not in self.supported_actions:
			raise Exception("Invalid action, supported : {}".format(self.supported_actions))

		if action == 'clear':
			self.driver.find_element_by_tag_name(tagname).clear()
		elif action == 'click':
			self.driver.find_element_by_tag_name(tagname).click()
		elif action == 'read_text':
			return self.driver.find_element_by_tag_name(tagname).text
		elif action == 'send_text':
			if text:
				self.driver.find_element_by_tag_name(tagname).send_keys(text)
			else:
				raise Exception("No text to send to browser")
		else:
			raise Exception("{} NOT IMPLEMENTED ERR".format(action))

		time.sleep(delay)

	
	def perform_by_linktext(self, linktext, action, text=None, delay=2):
		if action not in self.supported_actions:
			raise Exception("Invalid action, supported : {}".format(self.supported_actions))

		if action == 'clear':
			self.driver.find_element_by_link_text(linktext).clear()
		elif action == 'click':
			self.driver.find_element_by_link_text(linktext).click()
		elif action == 'read_text':
			return self.driver.find_element_by_link_text(linktext).text
		elif action == 'send_text':
			if text:
				self.driver.find_element_by_link_text(linktext).send_keys(text)
			else:
				raise Exception("No text to send to browser")
		else:
			raise Exception("{} NOT IMPLEMENTED ERR".format(action))

		time.sleep(delay)

	
	def perform_by_classname(self, classname, action, text=None, delay=2):
		if action not in self.supported_actions:
			raise Exception("Invalid action, supported : {}".format(self.supported_actions))

		if action == 'clear':
			self.driver.find_element_by_class_name(classname).clear()
		elif action == 'click':
			self.driver.find_element_by_class_name(classname).click()
		elif action == 'read_text':
			return self.driver.find_element_by_class_name(classname).text
		elif action == 'send_text':
			if text:
				self.driver.find_element_by_class_name(classname).send_keys(text)
			else:
				raise Exception("No text to send to browser")
		else:
			raise Exception("{} NOT IMPLEMENTED ERR".format(action))

		time.sleep(delay)

	
	def perform_by_xpath(self, xpath, action, text=None, delay=2):
		if action not in self.supported_actions:
			raise Exception("Invalid action, supported : {}".format(self.supported_actions))

		if action == 'clear':
			self.driver.find_element_by_xpath(xpath).clear()
		elif action == 'click':
			self.driver.find_element_by_xpath(xpath).click()
		elif action == 'read_text':
			return self.driver.find_element_by_xpath(xpath).text
		elif action == 'send_text':
			if text:
				self.driver.find_element_by_xpath(xpath).send_keys(text)
			else:
				raise Exception("No text to send to browser")
		else:
			raise Exception("{} NOT IMPLEMENTED ERR".format(action))

		time.sleep(delay)

	
	def refresh_browser(self):
		if self.driver:
			self.printlog("Refresing browser : {}".format(self.driver.title))
			self.driver.refresh()
			time.sleep(1)

	
	def close(self):
		if self.driver:
			self.driver.quit()
			self.printlog("Connection ended")
		else:
			self.printlog("No active connection found")


if __name__ == "__main__":
	from selenium.webdriver.common.keys import Keys

	def handler(signal_received, frame):
		# Handle any cleanup here
		msg = 'SIGINT or CTRL-C detected in main. Exiting gracefully'
		slot_finder.log_msg(msg)
		slot_finder.close()
		exit(0)

	signal(SIGINT, handler)

	CHROMEDRIVER_PATH = "C:\\Users\\prasannan\\Downloads\\chromedriver_win32\\chromedriver.exe"

	b = Browser(driverpath=CHROMEDRIVER_PATH)
	b.start(headless=False)
	b.load_url('https://google.com')
	xpath = '//*[@id="tsf"]/div[2]/div[1]/div[1]/div/div[2]/input'
	b.perform_by_xpath(xpath=xpath, action='send_text', text='nvidia')
	b.perform_by_xpath(xpath=xpath, action='send_text', text=Keys.DOWN)
	b.perform_by_xpath(xpath=xpath, action='send_text', text=Keys.RETURN)

	b.close()



