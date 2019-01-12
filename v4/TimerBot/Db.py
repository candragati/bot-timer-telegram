
import mysql.connector

class Db():
	def __init__(self, Bot):
		self.mysql = mysql.connector.connect(
		  host=Bot.config["database"]["host"],
		  port=Bot.config["database"]["port"],
		  user=Bot.config["database"]["username"],
		  passwd=Bot.config["database"]["password"],
		  database=Bot.config["database"]["db_name"]
		)
		self.cur = self.mysql.cursor()

	def close(self):
		self.mysql.close()

	def commit(self):
		self.mysql.commit()

	def __del__(self):
		self.close()
