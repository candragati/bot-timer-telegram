
import random
import importlib

class Language():
	def __init__(self, lang, fallback="En"):
		self.lang = lang
		self.fallback = fallback
	
	def get(self, block, key):
		me = __import__(
			"TimerBot.Languages.%s.%s" % (self.lang, block),
			fromlist=[""]
		)
		rv = me.rv()[key]
		if isinstance(rv, list):
			return random.choice(rv)
		else:
			return rv
