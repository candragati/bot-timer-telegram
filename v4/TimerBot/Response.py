
from telegram.ext import CommandHandler

class Response():
	def __init__(self, Bot):
		self.Bot = Bot

	def build(self):
		self.Bot.dp.add_handler(CommandHandler("start", self.start))

	def start(self, bot, update):
		print(update)
		try:
			__import__("TimerBot.Responses.Start", fromlist=[""]).Start(
				self.Bot,
				bot,
				update
			).run()
		except Exception as e:
			print("An error occured: %s " % (e))