#!/usr/bin/env python3

from TimerBot.Bot import Bot

with open("token.txt") as token:
    token = token.readlines()[0].strip()

Bot(token).run()

