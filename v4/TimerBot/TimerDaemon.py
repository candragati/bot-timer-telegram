
import cgi
import time
from telegram import Bot
from datetime import datetime
from TimerBot.Lang import Language

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;"
}

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

class TimerDaemon():
	def __init__(self, Bot_):
		self.Bot  = Bot_
		self.Bot_ = Bot(self.Bot.config["bot_token"])
		self.lang = Language("En")

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
			"SELECT `a`.`id`,`a`.`user_id`, (CASE WHEN `b`.`last_name` IS NULL THEN `b`.`first_name` ELSE  CONCAT(`b`.`first_name`, ' ', `b`.`last_name`) END), (CASE WHEN `b`.`username` IS NULL THEN '' ELSE CONCAT('(@', `b`.`username`,')') END), `a`.`chat_id`,`a`.`text`,`a`.`due_date`,`a`.`created_at` FROM `timer` AS `a`  INNER JOIN `users` AS `b` ON `a`.`user_id` = `b`.`id` WHERE `dispatched` = 0 AND `due_date` <= '%s' ORDER BY `due_date` ASC;" % (datetime.fromtimestamp(int(time.time())).strftime("%Y-%m-%d %H:%M:%S"))
		);
		self.queue = self.Db.cur.fetchall()

	def dispatch(self):
		ids = []
		i = txtd = ""
		for i in self.queue:
			txtd = self.lang.get("Timer", "timer_daemon.due",
				{
					":user_id": i[1],
					":name": html_escape(i[2]),
					":username": i[3],
					":text": html_escape(i[5]),
					":created_at": html_escape(str(i[6]))
				}
			)
			self.Bot_.sendMessage(chat_id=i[4], text=txtd, parse_mode="HTML")
			ids.append(i[0])

		if ids:
			ids = ",".join(str(x) for x in ids)
			self.Db.cur.execute("UPDATE `timer` SET `dispatched` = 1 WHERE `id` IN (%s);" % (ids));
			self.Db.commit()

		del i, ids, txtd

	def clean(self):
		del self.queue
