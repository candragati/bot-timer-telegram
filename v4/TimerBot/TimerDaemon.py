
import time
from telegram import Bot
from datetime import datetime

class TimerDaemon():
	def __init__(self, Bot_):
		self.Bot  = Bot_
		self.Bot_ = Bot(self.Bot.config["bot_token"])

	def run(self):
		while True:
			self.Db = self.Bot.initDb()
			self.fetch()
			self.dispatch()
			
			self.Bot.closeDb()
			self.clean()

			time.sleep(1)

	def fetch(self):
		self.Db.cur.execute(
			"SELECT `id`,`chat_id`,`text`,`due_date`,`created_at` FROM `timer` WHERE `dispatched` = 0 AND `due_date` <= '%s' ORDER BY `due_date` ASC" % (datetime.fromtimestamp(int(time.time())).strftime("%Y-%m-%d %H:%M:%S"))
		);
		self.queue = self.Db.cur.fetchall()

	def dispatch(self):
		ids = []
		for i in self.queue:
			self.Bot_.sendMessage(chat_id=i[1], text=i[2])
			ids.append(i[0])

		if ids:
			ids = ",".join(str(x) for x in ids)
			print(ids)
			query = "UPDATE `timer` SET `dispatched` = 1 WHERE `id` IN (%s);" % (ids);
			print(query)
			self.Db.cur.execute(query);
			self.Db.commit()

	def clean(self):
		del self.queue
