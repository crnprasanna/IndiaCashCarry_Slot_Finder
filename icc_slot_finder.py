
from helper.modules import *
from helper.logger import Logger
from helper.browser import Browser
from helper.sendemail import SendEmail
from helper.timeout import custom_decorator

import settings



class ICCSlotFinder:

	def __init__(self, printCFG=True):
		self.url = "https://www.indiacashandcarry.com/login"

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
		self.browser = Browser(driverpath=settings.CHROME_DRIVER_PATH, logger=self.logger)
		signal(SIGINT, self.handler)

		self.__validate_store__()
		self.email = SendEmail(settings.SENDER_GMAIL_ID, settings.SENDER_GMAIL_PASS)

		if printCFG:
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

	def handler(self, signal_received, frame):

		msg = 'SIGINT or CTRL-C detected. Exiting gracefully'
		self.log_msg(msg)
		self.close()
		sys.exit(0)


	def get_url(self, url, delay=3):
		self.browser.load_url(url, delay)


	def send_notification(self, subject, body):
		if settings.SEND_EMAIL and self.email:
			self.email.send_email(settings.SENDER_GMAIL_ID, settings.RECEIVER_EMAIL_ID, subject, body)


	@custom_decorator
	def start(self, withHead=False):
		try:
			self.browser.start(headless=(not withHead))
			self.get_url(self.url, delay=5)
		except Exception as err:
			self.log_msg('browser CANT LAUNCH, err {}\n'.format(err))
			self.close()
			sys.exit(0)

		self.log_msg('Attempting to login...')
		try:
			self.__login_icc_account__()
		except Exception as err:
			self.log_msg('LOGIN ERROR, CHECK CREDENTIALS, err: {}\n'.format(
				err))
			self.close()
			sys.exit(0)
		else:
			self.log_msg('Login succeeded')


	def __validate_store__(self):
		if self.icc_to_check not in self.supported_store_list:
			self.log_msg("Invalid option for ICC_STORES_TO_CHECK - {}".format(self.icc_to_check))
			self.close()
			self.exit(0)


	@custom_decorator
	def __login_icc_account__(self):
		xpath = '//*[@id="email"]'
		self.browser.perform_by_xpath(xpath, action='clear', delay=0.5)
		self.browser.perform_by_xpath(xpath, action='send_text', text=settings.ICC_LOGIN_EMAIL, delay=0.5)

		xpath = '/html/body/div[2]/div/div/div/div/div/div/div/form/div[2]/input'
		self.browser.perform_by_xpath(xpath, action='clear', delay=0.5)
		self.browser.perform_by_xpath(xpath, action='send_text', text=settings.ICC_LOGIN_PASS, delay=0.5)

		xpath = '/html/body/div[2]/div/div/div/div/div/div/div/form/div[3]/button'
		self.browser.perform_by_xpath(xpath, action='click', delay=3)

		try:
			xpath = '/html/body/div[2]/div/div/div/div/div/div/div/form/div[3]/div'
			status = self.browser.perform_by_xpath(xpath, action='read_text')
			if 'Incorrect username' in status:
				self.log_msg('LOGIN ERROR, CHECK CREDENTIALS')
				self.close()
				sys.exit(0)
		except Exception:
			pass

		try:
			xpath = '//*[@id="email-error"]'
			status = self.browser.perform_by_xpath(xpath, action='read_text')
			self.log_msg('LOGIN ERROR, CHECK EMAIL ID')
			self.close()
			sys.exit(0)
		except Exception:
			pass


	def log_msg(self, msg):
		self.logger.log(msg)


	@custom_decorator
	def __pass_zip__(self, inp_zip):
		xpath = '//*[@id="autocomplete"]'
		self.browser.perform_by_xpath(xpath, action='clear', delay=0.5)
		self.browser.perform_by_xpath(xpath, action='send_text', text=inp_zip, delay=0.5)
		self.browser.perform_by_xpath(xpath, action='send_text', text=Keys.DOWN, delay=0.5)
		self.browser.perform_by_xpath(xpath, action='send_text', text=Keys.RETURN, delay=0.5)

	@custom_decorator
	def __find_icc_store_list__(self):
		self.__pass_zip__(self.default_zip)

		out = [x.text for (i, x) in enumerate(self.browser.driver.find_elements_by_tag_name('li')) if x.text and len(x.text.split(" ")) > 3]

		self.addr_list = [ (self.default_zip, out[0]) ]
		for addr in out[1:]:
			self.addr_list.append(( addr[-5:], addr))


	@custom_decorator
	def __find_actual_icc_list__(self):
		store_map = {'SUNNYVALE' : '94087', 'SAN JOSE' : '95129', 'FREMONT' : '94538' }
		if self.icc_to_check == "ALL":
			try:
				self.__find_icc_store_list__()
			except TimeoutError:
				self.log_msg("TIMEOUT ERROR WITH FIND ICC STORE LIST")
				self.close()
				raise Exception("Restart program - Timeout ERR")
			except Exception as err:
				self.log_msg('RUNTIME ERROR WITH ICC STORE LIST, \
				Err: {}'.format(err))
				self.close()
				raise Exception("Restart program")
		else:
			self.addr_list = [(store_map[self.icc_to_check], self.icc_to_check)]


	@custom_decorator
	def __switch_store__(self, new_zip):
		url = "https://www.indiacashandcarry.com/"
		self.get_url(url, delay=3)

		self.browser.perform_by_classname('header-location', action='click', delay=1)

		try:
			xpath = '//*[@id="price-list-0"]/p/a'
			self.browser.perform_by_xpath(xpath, action='click', delay=2)

			self.__pass_zip__(new_zip)
			return True

		except Exception:
			pass


		try:
			xpath = '//*[@id="price-list-1"]/p/a'
			self.browser.perform_by_xpath(xpath, action='click', delay=2)

			self.__pass_zip__(new_zip)
			return True
		except Exception:
			pass


		try:
			xpath = '//*[@id="price-list-2"]/p/a'
			self.browser.perform_by_xpath(xpath, action='click', delay=2)

			self.__pass_zip__(new_zip)
			return True
		except Exception as err:
			pass

		return False


	@custom_decorator
	def __select_store__(self):
		try:
			time.sleep(2)
			self.browser.perform_by_linktext('Select This Location', action='click', delay=2)

			xpath = '//*[@id="price-list-0"]/ul/li[1]/p'
			self.browser.perform_by_xpath(xpath, action='click', delay=2)
		except Exception as err:
			raise Exception(err)

	@custom_decorator
	def __check_pickup_slot__(self):
		try:
			xpath = '/html/body/div[2]/section/div/div/div[3]/div/ul/li[1]/div'
			self.browser.perform_by_xpath(xpath, action='click')
		except:
			xpath = '/html/body/div[2]/section/div/div/div[2]/div/ul/li[1]/div/h3'
			self.browser.perform_by_xpath(xpath, action='click')

		time.sleep(0.5)
		try:
			xpath = '/html/body/div[2]/section/div/div/div[1]'
			store_msg = self.browser.perform_by_xpath(xpath, action='read_text')

			if 'Checkout Continue Shopping' in store_msg:
				xpath = '/html/body/div[2]/section/div/div/div[2]/div/div/div'
				store_msg = self.browser.perform_by_xpath(xpath, action='read_text')
				return False
			else:
				return True


		except Exception as err:
			print("Execption found with finding PICKUP slot, err : {}\n".format(err))


	@custom_decorator
	def __check_delivery_slot__(self):

		if not self.__min_order_met__():
			if self.icc_option == "BOTH":
				return False
			else:
				self.close()
				self.log_msg("\nProgram Ended\n")
				sys.exit(0)

		try:
			xpath = '/html/body/div[2]/section/div/div/div[3]/div/ul/li[2]/div/h3'
			self.browser.perform_by_xpath(xpath, action='click')
		except:
			xpath = '/html/body/div[2]/section/div/div/div[2]/div/ul/li[2]/div'
			self.browser.perform_by_xpath(xpath, action='click')

		time.sleep(0.5)
		try:
			xpath = '/html/body/div[2]/section/div/div/div[1]'
			store_msg = self.browser.perform_by_xpath(xpath, action='read_text')
			if 'Delivery is not available' in store_msg or 'Checkout Continue Shopping' in store_msg:
				return False
			else:
				return True


		except Exception as err:
			print("Execption found with finding DELIVERY slot, err : {}\n".format(err))

	@custom_decorator
	def __is_cart_empty__(self):
		try:
			xpath = '/html/body/div[2]/section/div/div/div/div/h4'
			status = self.browser.perform_by_xpath(xpath, action='read_text')

			if 'Your cart is empty' in status:
				self.log_msg("EMPTY_CART ERROR, CAN't CHECK SLOT")
				self.close()
				sys.exit(0)
		except Exception:
			pass


	@custom_decorator
	def __min_order_met__(self):
		try:
			xpath = '/html/body/div[2]/section/div/div/div[1]/div/p'
			status = self.browser.perform_by_xpath(xpath, action='read_text')
			if 'All Delivery orders must be' in status:
				self.log_msg("MIN_CART_NOT_MET ERROR, CAN't CHECK  DELIVERY SLOT")
				return False
			else:
				return True
		except Exception:
			return True

	@custom_decorator
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
			self.get_url(url, delay=5)

			self.__is_cart_empty__()

			if any ( (self.icc_option == "BOTH", self.icc_option == "DELIVERY" )):
				self.delivery_status[store] = False
				status = self.__check_delivery_slot__()
				self.delivery_status[store] = status

			if any ( (self.icc_option == "BOTH", self.icc_option == "PICKUP" )):
				self.pickup_status[store] = False
				status = self.__check_pickup_slot__()
				self.pickup_status[store] = status


	@custom_decorator
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


	def refresh_browser(self):
		if self.browser:
			self.browser.refresh()
			time.sleep(1)

	def close(self):
		if self.browser:
			self.chk_slot_status()
			self.browser.close()
			self.email.close()
			self.email = None
			self.browser = None
			self.log_msg('\n##########################################')



if __name__ == '__main__':

	def handler(signal_received, frame):

		msg = 'SIGINT or CTRL-C detected in main. Exiting gracefully'
		slot_finder.log_msg(msg)
		slot_finder.close()
		sys.exit(0)

	signal(SIGINT, handler)

	slot_finder = ICCSlotFinder()
	slot_finder.start(withHead=True)

	INTERVAL_BETWEEN_LOOPS = 60 # sec

	heartbeat = datetime.now()
	HEARTBEAT_PERIOD = (4*60) #mins


	while True:

		slot_finder.log_msg('\nStarting new loop')
		try:
			slot_finder.find_slots()
		except Exception:
			ticks = (datetime.now() - heartbeat) / timedelta(minutes=HEARTBEAT_PERIOD)
			if (ticks > 1):
				slot_finder.log_msg('\nSending email in Heartbeat status..')
				slot_finder.send_notification("ICC SLot Finder -Hearbeat status", "No Slot found")
				heartbeat = datetime.now()

			slot_finder.close()
			time.sleep(INTERVAL_BETWEEN_LOOPS)

			slot_finder.log_msg('\nRUNTIME ERR HANDLED, Creating new instance..\n')
			slot_finder = ICCSlotFinder(printCFG=False)
			slot_finder.start()
			continue

		if slot_finder.chk_slot_status():
			slot_finder.log_msg('\nSlot found...')
			
			slot_finder.send_notification("ICC Slot Finder - SLOT FOUND", slot_finder.slots_result)
			break

		ticks = (datetime.now() - heartbeat) / timedelta(minutes=HEARTBEAT_PERIOD)
		if (ticks > 1):
			slot_finder.log_msg('\nSending email in Heartbeat status..')
			slot_finder.send_notification("ICC Slot Finder - Hearbeat status", slot_finder.slots_result)
			heartbeat = datetime.now()


		url = "https://www.indiacashandcarry.com/"
		slot_finder.get_url(url)

		slot_finder.browser.refresh_browser()
		time.sleep(INTERVAL_BETWEEN_LOOPS)

	slot_finder.close()
	slot_finder.log_msg('Program ended\n')
