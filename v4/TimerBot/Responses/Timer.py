
import re
import json
import time
from datetime import datetime
from TimerBot.Response import ResponseFoundation

class SetTimer(ResponseFoundation):

    def needDb(self):
        return True

    def run(self):
        me = re.compile("^([0-9]+)(.*)").findall(self.rd[0])
        if me:
            error = False

            add = int(me[0][0])
            me = me[0][1].lower().strip()
            unixtime = int(time.time())

            if me == "h":
                add = add * 3600
            elif me == "m":
                add = add * 60
            elif me == "s" or me == "":
                pass
            else:
                error = True
            if not error:
                textd = self.rd[1].strip()
                add = datetime.fromtimestamp(unixtime + add).strftime("%Y-%m-%d %H:%M:%S")
                unixtime = datetime.fromtimestamp(unixtime).strftime("%Y-%m-%d %H:%M:%S")
                self.Db.cur.execute(
                    "INSERT INTO `timer` (`user_id`, `chat_id`, `text`, `dispatched`, `due_date`, `created_at`) VALUES (%s, %s, %s, %s, %s, %s);",
                    (
                        self.update["message"]["from_user"]["id"],
                        self.update["message"]["chat"]["id"],
                        textd,
                        0,
                        add,
                        unixtime
                    )
                )
                self.Db.commit()

                r = self.lang.get("Timer", "set_timer.ok",
                    {
                        ":text": textd,
                        ":created_at": unixtime,
                        ":due_date": add
                    }
                )
                del textd, unixtime, add
            else:
                r = self.lang.get("Timer", "set_timer.error_unit_format") % (me)

            del me, error
        else:
            r = self.lang.get("Timer", "set_timer.help")


        self.update.message.reply_text(r)
        return True
