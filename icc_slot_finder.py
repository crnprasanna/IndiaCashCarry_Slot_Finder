from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import sys
import time
import settings
from logger import Logger
import smtplib
from email.mime.text import MIMEText
import timeout
import timeout_decorator
from signal import signal, SIGINT


class ICCSlotFinder:

	def __init__(self):
		self.url = "https://www.indiacashandcarry.com/login"

		self.browser = None
		self.default_zip = '94040'
		self.slots_result = ''
		self.addr_list = []
		self.pickup_status = {}
		self.firstInstance = True
		self.delivery_status = {}
		self.icc_to_check = settings.ICC_STORES_TO_CHECK.upper()
		self.icc_option = settings.ICC_STATUS_TO_CHECK.upper()

		self.supported_store_list = [ 'SUNNYVALE', 'SAN JOSE', 'FREMONT', 'ALL' ]

		self.logger = Logger()
		signal(SIGINT, self.handler)

	def handler(self, signal_received, frame):

		msg = 'SIGINT or CTRL-C detected. Exiting gracefully'
		self.log_msg(msg)
		self.close_connection()

		sys.exit(0)

	@timeout.custom_decorator
	def start_browser(self):
		self.log_msg('\n##########################################')
		self.log_msg('Input Config:')
		self.log_msg('\tChrome driver path: {}'.format(
			settings.CHROME_DRIVER_PATH))
		self.log_msg('\tStores List: {}'.format(self.icc_to_check))
		self.log_msg('\tPickup/Delivery: {}'.format(self.icc_option))
		self.log_msg('\tICC Login: {}'.format(
			settings.ICC_LOGIN_EMAIL))
		self.log_msg('\tSEND_EMAIL report: {}'.format(
			settings.SEND_EMAIL))
		self.log_msg('\n##########################################')

		try:
			self.__validate_store__()
			self.__init_browser__()
		except Exception as err:
			self.log_msg('browser CANT LAUNCH, err {}\n'.format(err))
			self.close_connection()
			sys.exit(0)

		self.log_msg('Attempting to login...')
		try:
			self.__login_icc_account__()
		except Exception as err:
			self.log_msg('LOGIN ERROR, CHECK CREDENTIALS, err: {}\n'.format(
				err))
			self.close_connection()
			sys.exit(0)
		else:
			self.log_msg('Login succeeded')


	def __validate_store__(self):
		if self.icc_to_check not in self.supported_store_list:
			raise Exception("Invalid option for ICC_STORES_TO_CHECK - {}".format(self.icc_to_check))


	@timeout.custom_decorator
	def __init_browser__(self):
		options = webdriver.ChromeOptions()
		options.add_argument('--headless')
		options.add_argument('log-level=3')
		options.add_argument('window-size=1920,1080')
		options.add_argument('--no-sandbox')
		options.add_argument('--single-process')

		capabilities = DesiredCapabilities.CHROME.copy()
		capabilities['acceptSslCerts'] = True
		capabilities['acceptInsecureCerts'] = True

		self.browser = webdriver.Chrome(executable_path=settings.CHROME_DRIVER_PATH, chrome_options=options, desired_capabilities=capabilities)
		#self.browser = webdriver.Chrome(executable_path=settings.CHROME_DRIVER_PATH)

		self.browser.delete_all_cookies()
		self.browser.get(self.url)
		time.sleep(5)


	@timeout.custom_decorator
	def __login_icc_account__(self):
		xpath = '//*[@id="email"]'
		self.browser.find_element_by_xpath(xpath).clear()
		time.sleep(0.5)
		self.browser.find_element_by_xpath(xpath).send_keys(settings.ICC_LOGIN_EMAIL)
		time.sleep(0.5)

		xpath = '/html/body/div[2]/div/div/div/div/div/div/div/form/div[2]/input'
		self.browser.find_element_by_xpath(xpath).clear()
		time.sleep(0.5)
		self.browser.find_element_by_xpath(xpath).send_keys(settings.ICC_LOGIN_PASS)
		time.sleep(0.5)

		xpath = '/html/body/div[2]/div/div/div/div/div/div/div/form/div[3]/button'
		self.browser.find_element_by_xpath(xpath).click()
		time.sleep(3)

		try:
			xpath = '/html/body/div[2]/div/div/div/div/div/div/div/form/div[3]/div'
			status = self.browser.find_element_by_xpath(xpath).text
			if 'Incorrect username' in status:
				raise Exception("Check ICC store username/password")
		except:
			pass


	def log_msg(self, msg):
		self.logger.log(msg)


	@timeout.custom_decorator
	def __send_email__(self, slot_found_flag):
		msg = MIMEText(self.slots_result)
		if slot_found_flag:
			msg['Subject'] = 'ICC slot information : SLOT_FOUND'
		else:
			msg['Subject'] = \
				'ICC slot information : SLOT_NOT_FOUND'

		msg['From'] = settings.SENDER_GMAIL_ID
		msg['To'] = settings.RECEIVER_EMAIL_ID
		server = None

		try:
			server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			server.login(settings.SENDER_GMAIL_ID,
							  settings.SENDER_GMAIL_PASS)
			server.sendmail(settings.SENDER_GMAIL_ID,
								 settings.RECEIVER_EMAIL_ID,
								 msg.as_string())
			self.log_msg("Email notification succesfully sent")
		except Exception as err:
			self.log_msg('Exception with sending email, err : {}'.format(
				err))
			self.log_msg('Continuing finding slots.. check status from \
			console logs...')

		try:
			if server:
				server.quit()
		except Exception:
			pass


	@timeout.custom_decorator
	def __pass_zip__(self, inp_zip):
		xpath = '//*[@id="autocomplete"]'
		element = self.browser.find_element_by_xpath(xpath)
		element.clear()
		time.sleep(0.5)
		element.send_keys(inp_zip)
		time.sleep(0.5)
		element.send_keys(Keys.DOWN)
		time.sleep(0.5)
		element.send_keys(Keys.RETURN)
		time.sleep(0.5)

	@timeout.custom_decorator
	def __find_icc_store_list__(self):
		self.__pass_zip__(self.default_zip)

		out = [x.text for (i, x) in enumerate(self.browser.find_elements_by_tag_name('li')) if x.text and len(x.text.split(" ")) > 3]

		self.addr_list = [ (self.default_zip, out[0]) ]
		for addr in out[1:]:
			self.addr_list.append(( addr[-5:], addr))


	@timeout.custom_decorator
	def __find_actual_icc_list__(self):
		store_map = {'SUNNYVALE' : '94087', 'SAN JOSE' : '95129', 'FREMONT' : '94538' }
		if self.icc_to_check == "ALL":
			try:
				self.__find_icc_store_list__()
			except timeout_decorator.TimeoutError:
				self.log_msg("TIMEOUT ERROR WITH FIND ICC STORE LIST")
				self.close_connection()
				raise Exception("Restart program - Timeout ERR")
			except Exception as err:
				self.log_msg('RUNTIME ERROR WITH ICC STORE LIST, \
				Err: {}'.format(err))
				self.close_connection()
				raise Exception("Restart program")
		else:
			self.addr_list = [(store_map[self.icc_to_check], self.icc_to_check)]


	@timeout.custom_decorator
	def __switch_store__(self, new_zip):
		url = "https://www.indiacashandcarry.com/"
		self.browser.get(url)
		time.sleep(3)

		self.browser.find_element_by_class_name('header-location').click()
		time.sleep(1)

		try:
			xpath = '//*[@id="price-list-0"]/p/a'
			self.browser.find_element_by_xpath(xpath).click()

			time.sleep(2)
			self.__pass_zip__(new_zip)
			return True

		except Exception:
			pass


		try:
			xpath = '//*[@id="price-list-1"]/p/a'
			self.browser.find_element_by_xpath(xpath).click()

			time.sleep(2)
			self.__pass_zip__(new_zip)
			return True
		except Exception:
			pass


		try:
			xpath = '//*[@id="price-list-2"]/p/a'
			self.browser.find_element_by_xpath(xpath).click()

			time.sleep(2)
			self.__pass_zip__(new_zip)
			return True
		except Exception as err:
			pass

		return False


	@timeout.custom_decorator
	def __select_store__(self):
		try:
			time.sleep(2)
			self.browser.find_element_by_link_text("Select This Location").click()
			time.sleep(2)

			xpath = '//*[@id="price-list-0"]/ul/li[1]/p'
			self.browser.find_element_by_xpath(xpath).click()
			time.sleep(2)
		except Exception as err:
			self.browser.save_screenshot("sel_store.png")
			raise Exception(err)

	@timeout.custom_decorator
	def __check_pickup_slot__(self):
		try:
			xpath = '/html/body/div[2]/section/div/div/div[3]/div/ul/li[1]/div'
			self.browser.find_element_by_xpath(xpath).click()
		except:
			xpath = '/html/body/div[2]/section/div/div/div[2]/div/ul/li[1]/div/h3'
			self.browser.find_element_by_xpath(xpath).click()

		time.sleep(0.5)
		try:
			xpath = '/html/body/div[2]/section/div/div/div[1]'
			store_msg = self.browser.find_element_by_xpath(xpath).text

			if 'Checkout Continue Shopping' in store_msg:
				xpath = '/html/body/div[2]/section/div/div/div[2]/div/div/div'
				store_msg = self.browser.find_element_by_xpath(xpath).text
				return False
			else:
				return True


		except Exception as err:
			print("Execption found with finding PICKUP slot, err : {}\n".format(err))


	@timeout.custom_decorator
	def __check_delivery_slot__(self):

		if not self.__min_order_met__():
			if self.icc_option == "BOTH":
				return False
			else:
				self.close_connection()
				self.log_msg("\nProgram Ended\n")
				sys.exit(0)

		try:
			xpath = '/html/body/div[2]/section/div/div/div[3]/div/ul/li[2]/div/h3'
			self.browser.find_element_by_xpath(xpath).click()
		except:
			xpath = '/html/body/div[2]/section/div/div/div[2]/div/ul/li[2]/div'
			self.browser.find_element_by_xpath(xpath).click()

		time.sleep(0.5)
		try:
			xpath = '/html/body/div[2]/section/div/div/div[1]'
			store_msg = self.browser.find_element_by_xpath(xpath).text
			if 'Delivery is not available' in store_msg or 'Checkout Continue Shopping' in store_msg:
				return False
			else:
				return True


		except Exception as err:
			print("Execption found with finding DELIVERY slot, err : {}\n".format(err))

	@timeout.custom_decorator
	def __is_cart_empty__(self):
		try:
			xpath = '/html/body/div[2]/section/div/div/div/div/h4'
			status = self.browser.find_element_by_xpath(xpath).text
			if 'Your cart is empty' in status:
				self.log_msg("EMPTY_CART ERROR, CAN't CHECK SLOT")
				self.close_connection()
				sys.exit(0)
		except Exception:
			pass


	@timeout.custom_decorator
	def __min_order_met__(self):
		try:
			xpath = '/html/body/div[2]/section/div/div/div[1]/div/p'
			status = self.browser.find_element_by_xpath(xpath).text
			if 'All Delivery orders must be' in status:
				self.log_msg("MIN_CART_NOT_MET ERROR, CAN't CHECK  DELIVERY SLOT")
				return False
			else:
				return True
		except Exception:
			return True

	@timeout.custom_decorator
	def find_slots(self):
		self.__find_actual_icc_list__()

		for (zp, address) in self.addr_list:
			if self.icc_to_check == "ALL":
				selected_store = address[:address.index(' Select')]
			else:
				selected_store = address

			if any( ('DE ANZA' in selected_store, 'SAN JOSE' in selected_store) ):
				store = 'SAN JOSE'
			else:
				store = selected_store

			self.log_msg("Attempting to find slot for Store : {}".format(selected_store))

			if not self.firstInstance :
				if not self.__switch_store__(zp):
					raise Exception("RUNTIME ERR IN SWITCH STORE")
			else:
				self.firstInstance = False

			self.__select_store__()
			url = 'https://www.indiacashandcarry.com/cart/checkout'
			self.browser.get(url)
			time.sleep(5)

			self.__is_cart_empty__()

			if any ( (self.icc_option == "BOTH", self.icc_option == "DELIVERY" )):
				self.delivery_status[store] = False
				status = self.__check_delivery_slot__()
				self.delivery_status[store] = status

			if any ( (self.icc_option == "BOTH", self.icc_option == "PICKUP" )):
				self.pickup_status[store] = False
				status = self.__check_pickup_slot__()
				self.pickup_status[store] = status



	@timeout.custom_decorator
	def chk_slot_status(self):
		is_slot_found = False
		self.slots_result = ''

		self.log_msg("\nSlot status:")
		self.slots_result += "\nSlot Status:\n"

		for (store, status) in self.delivery_status.items():
			self.log_msg("\t{} Delivery Slot : {}".format(store, status))
			self.slots_result += "\t{} Delivery Slot : {}\n".format(store, status)

			if status:
				is_slot_found = True

		self.slots_result += "\n"

		for (store, status) in self.pickup_status.items():
			self.log_msg("\t{} Pickup Slot : {}".format(store, status))
			self.slots_result += "\t{} PickUp Slot : {}\n".format(store, status)

			if status:
				is_slot_found = True

		self.log_msg("\n")
		self.slots_result += "\n"
		return is_slot_found


	def send_email(self, slot_found_status):
		if settings.SEND_EMAIL:
			self.__send_email__(slot_found_status)

	def refresh_browser(self):
		if self.browser:
			self.browser.refresh()
			time.sleep(1)

	def close_connection(self):
		if self.browser:
			self.browser.quit()
			self.log_msg('Connection ended')

		self.log_msg('\n##########################################')



if __name__ == '__main__':

	def handler(signal_received, frame):

		msg = 'SIGINT or CTRL-C detected in main. Exiting gracefully'
		slot_finder.log_msg(msg)
		slot_finder.close_connection()
		sys.exit(0)

	signal(SIGINT, handler)

	slot_finder = ICCSlotFinder()
	slot_finder.start_browser()

	INTERVAL_BETWEEN_LOOPS = 6  # sec

	while True:

		slot_finder.log_msg('Starting new loop')
		try:
			slot_finder.find_slots()
		except Exception:
			slot_finder.close_connection()
			slot_finder.log_msg('\nCreating new instance..\n')
			slot_finder = ICCSlotFinder()
			slot_finder.start_browser()
			continue

		if slot_finder.chk_slot_status():
			slot_finder.log_msg('\nSlot found...')
			slot_finder.send_email(True)
			break

		url = "https://www.indiacashandcarry.com/"
		slot_finder.browser.get(url)

		slot_finder.refresh_browser()
		time.sleep(INTERVAL_BETWEEN_LOOPS)

	slot_finder.close_connection()
	slot_finder.log_msg('Program ended\n')
