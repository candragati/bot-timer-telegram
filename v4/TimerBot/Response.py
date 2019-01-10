
from telegram.ext import CommandHandler

class Response():
	def __init__(self, Bot):
		self.Bot = Bot

	def build(self):
		self.Bot.dp.add_handler(CommandHandler("start", self.start))

	def start(self, bot, update):
		print("start", update);
		__import__("TimerBot.Responses.Start").Start(self.Bot, bot, update).run()