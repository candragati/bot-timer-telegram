
import re
from TimerBot.Lang import Language
from telegram.ext import MessageHandler, Filters

class ResponseFoundation():
	def __init__(self, Bot, bot, update, rd, lang):
		self.Bot = Bot
		self.bot = bot
		self.update = update
		self.rd = rd
		self.lang = lang

class Response():
	def __init__(self, Bot):
		self.Bot = Bot

	def build(self):
		self.Bot.dp.add_handler(MessageHandler((Filters.text | Filters.command), self.res))

	def res(self, bot, update):
		try:
			self.text = update["message"]["text"]
			
			ri = self.getRiText()

			try:
				getattr(__import__(
					"TimerBot.Responses.%s" % (ri[0]), 
					fromlist=[""]
				), ri[1])(
					self.Bot,
					bot,
					update,
					ri[2],
					Language("En")
				).run()
			except Exception as e:
				print("An error occured: %s " % (e))
		except Exception as e:
			print("An error occured: %s " % (e))
	
	def getRiText(self):
		RiList = {
			"^[\/\.\!\~]start": ["Start", "Start"],
			"(?:^[\/\.\!\~]set)((?:[\s]).+)?((?:[\s]).+)?$": ["SetTimer", "SetTimer"]
		};

		for i in RiList:
			me = re.compile(i).findall(self.text)
			if me:
				rd = RiList[i]
				rd.append(me)
				return rd
