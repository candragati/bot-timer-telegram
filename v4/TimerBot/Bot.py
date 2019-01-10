
from telegram.ext import Updater
from TimerBot.Response import Response

class Bot():
	def __init__(self, token):
		print(token)
		self.updater = Updater(token)
		self.dp = self.updater.dispatcher
		self.buildResponses()

	def buildResponses(self):
		Response(self).build()

	def run(self):
		print("Running...")
		self.updater.start_polling()
		self.updater.idle()
