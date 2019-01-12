
from TimerBot.Response import ResponseFoundation

class Start(ResponseFoundation):

	def needDb():
		return False

	def run(self):

		if self.update["message"]["chat"]["type"] == "private":
			r = self.lang.get("Start", "private")
		else:
			r = self.lang.get("Start", "group")

		self.update.message.reply_text(r)
