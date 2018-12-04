# bot-timer-telegram
>telegram bot timer

[![](https://img.shields.io/badge/Telegram-Account-blue.svg)](https://t.me/srabatsrobot)
![](https://img.shields.io/badge/Python-3-green.svg)

*pengembangan dari file timer.py pada folder example python-telegram-bot*

## usage example:

**`/set 5 oke`** = 5 detik kemudian bot menulis 'oke'

**`/set 5s oke`** = 5 detik kemudian bot menulis 'oke'

**`/set 5m oke`** = 5 menit kemudian bot menulis 'oke'

**`/set 5h oke`** = 5 jam kemudian bot menulis 'oke'

**`/set 5j oke`** = 5 jam kemudian bot menulis 'oke'



**`/set 13:00:00 oke`** = pada pukul 13:00:00 bot menulis 'oke'

**`/set 2018-12-11 01:02:03 oke`** = pada tanggal 11 desember 2018, jam 01:02:03 bot menulis 'oke'


## jadwal sholat:
**`/set sholat <nama kota>`**<br>
_cek daftar nama2 kota yang tersedia di https://api.banghasan.com/sholat/format/json/kota_

## cek agenda
**`/agenda`**

## todo  
 - [x] jadwal sholat
 - [x] penambahan timer dengan format jam
 - [x] penambahan timer dengan format tanggal
 - [x] pembuatan database
 - [ ] hapus timer
 - [ ] repeated timer


#### change log
- 30-11-2018 : hari jum'at, sholat dzuhur berubah menjadi sholat jumat
- 25-11-2018 : khusus hari minggu, bot akan menggunakan bahasa inggris (mengikuti rules pada group @KodingTeh)
- 18-11-2018 : random footnote untuk jadwal sholat
- 19-11-2018 : tambah fitur jadwal sholat
- 15-11-2018 : tambah fitur agenda
- 13-11-2018 : timerbot versi 3 mulai menggunakan database sqlite
- 02-11-2018 : fix bug markdown. thanks @MuhShalah007
