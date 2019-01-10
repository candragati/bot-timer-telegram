
from TimerBot.Response import ResponseFoundation

class Start(ResponseFoundation):
	def run(self):
		self.update.message.reply_text(self.lang.get("Start", "ok"))