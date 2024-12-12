from flask import Flask, render_template, request
from flask_ngrok2 import run_with_ngrok
# from tg_file_id.file_id import PhotoFileId
import sqlite3

app = Flask(__name__, static_url_path="/static")
run_with_ngrok(app, auth_token="5AiDcEAVFTE8nUJ7MtYAq_45faXNchQ7TqRwmCpvNDF")


@app.route('/')
def media():
	connect = sqlite3.connect('database')
	cursor = connect.cursor()
	cursor.execute("SELECT media_tipe,media_keyword, media_id,thumb_id, image_size FROM media WHERE chat_id = '-1001162202776'")

	data = cursor.fetchall()
	
	
	return render_template("participants.html", data=data)


if __name__ == '__main__':	
	app.run()
