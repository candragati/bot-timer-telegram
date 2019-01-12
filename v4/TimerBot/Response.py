
import re
from TimerBot.Lang import Language
from TimerBot.ResponseRoutes import RiList
from telegram.ext import MessageHandler, Filters

class ResponseFoundation():
	def __init__(self, Bot, bot, update, rd, lang):
		self.Bot = Bot
		self.bot = bot
		self.update = update
		self.rd = rd
		self.lang = lang
	
	def setDbHandler(self, Db):
		self.Db = Db

class Response():
	def __init__(self, Bot):
		self.Bot = Bot

	def build(self):
		self.Bot.dp.add_handler(MessageHandler((Filters.text | Filters.command), self.res))

	def res(self, bot, update):
		global RiList
		try:
			for i in RiList:
				me = []
				try:
					me = re.compile(i).findall(update["message"]["text"])
				except:
					break

				if me:
					rd = RiList[i]
					rbp = getattr(__import__(
						"TimerBot.Responses.%s" % (rd[0]), 
						fromlist=[""]
					), rd[1])(
						self.Bot,
						bot,
						update,
						me[0],
						Language("En")
					)
					
					if rbp.needDb():
						rbp.setDbHandler(self.Bot.initDb())
						rbp = rbp.run()
						self.Bot.closeDb()
					else:
						rbp = rbp.run()


					if rbp:
						break

		except Exception as e:
			print("An error occured: %s " % (e))