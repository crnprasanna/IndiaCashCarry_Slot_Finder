
if __name__ != '__main__':
	from helper.modules import *
else:
	from modules import *


class SendEmail():
	def __init__(self, gmail_id, gmail_pass):
		self.id = gmail_id
		self.password = gmail_pass
		self.server = None


	def __login__(self):
		try:
			self.server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			self.server.login(self.id, self.password)

			#print("Logged in successfully")
		except Exception as err:
			print('Exception with login, err : {}'.format(
				err))
			raise Exception(err)

	def send_email(self, sender, receiver, sub, body):
		try:
			self.__login__()

			msg = MIMEText(body)
			msg['Subject'] = sub
			msg['From'] = sender
			msg['To'] = receiver

			self.server.sendmail(sender, receiver, msg.as_string())
			print("Email notification succesfully sent")

			self.__close__()
		except Exception as err:
			print('Exception with sending email, err : {}'.format(
				err))
			raise Exception(err)


	def __close__(self):
		try:
			if self.server:
				self.server.quit()
		except Exception:
			pass


if __name__ == "__main__":
	email = SendEmail('gmail_id', 'gmail_pass')
	email.send_email('sender', 'receiver', 'sub', 'body')

