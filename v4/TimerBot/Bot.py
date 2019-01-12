
import os
import sys
from TimerBot.Db import Db
from telegram.ext import Updater
from TimerBot.Response import Response
from TimerBot.TimerDaemon import TimerDaemon

class Bot():
	def __init__(self, config):
		self.config = config
		del config

	def run(self):
		print("Running master handler...")

		timerDaemonPid = os.fork()
		if  timerDaemonPid == 0:
			del timerDaemonPid
			print("Running timer daemon...")
			TimerDaemon(self).run()
			sys.exit(0)

		telegramDaemonPid = os.fork()
		if telegramDaemonPid == 0:
			del timerDaemonPid, telegramDaemonPid
			print("Running telegram daemon...")
			
			self.updater = Updater(self.config["bot_token"])
			self.dp = self.updater.dispatcher

			Response(self).build()

			self.updater.start_polling()
			self.updater.idle()
			sys.exit(0)

		status = 0
		os.wait()

	def initDb(self):
		self.Db = Db(self)
		return self.Db

	def closeDb(self):
		self.Db.close()
