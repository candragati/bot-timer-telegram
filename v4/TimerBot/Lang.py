
import random
import importlib

class Language():
	def __init__(self, lang, fallback="En"):
		self.lang = lang
		self.fallback = fallback
	
	def get(self, block, key, bind={}):
		me = __import__(
			"TimerBot.Languages.%s.%s" % (self.lang, block),
			fromlist=[""]
		)
		rv = me.rv()[key]
		if isinstance(rv, list):
			return self.bindd(random.choice(rv), bind)
		else:
			return self.bindd(rv, bind)

	def bindd(self, strd, bind={}):
		for i in bind:
			strd = strd.replace(str(i), str(bind[i]))
		return strd
