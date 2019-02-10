import datetime
import random

def kamus(teks):
        a = {
            "qotd_mogok":{
                "id":   ["Silahkan reply atau forward chat yang akan di quote"],
                "en":   ["Please reply or forward a quotable chat."],
            },
            "qotd_dobel":{
                "id":   ["Dobel quote dengan ID nomor %s"],
                "en":   ["Duplicate quote with ID %s"]
            },
            "dqotd_sukses":{
                "id":   ["Berhasil di dequote"],
                "en":   ["dequote success!"],                
            },
            "dqotd_not_found":{
                "id":   ["Kok ID nya gak ada ya? Yakin udah bener?"],
                "en":   ["ID not found"],
            },
            "quote_kurang":{
                "id":   ["Silahkan tambahin dengan ID nya."],
                "en":   ["Please add it with ID"]
            },
            "quote_not_found":{
                "id":   ["ID nya gak ketemu. Mungkin sudah dihapus atau udah mentok."],
                "en":   ["ID not found"]
            },
            "quote_mogok":{
                "id":   ["Gak bisa simpen quote, liat errornya di bawah ini"],
                "en":   ["Cannot saved quote. See error below."]
            },
            "quote_simpan":{
                "id":   ["Quote disimpan dengan id %s\nuntuk lihat, ketik /qotd %s\nuntuk dequote, ketik /dqotd %s"],
                "en":   ["Quote saved with id %s\nto see quote : /qotd %s\nto dequote : /dqotd %s"]
            },
            "mogok":   {
                "id":  [
                    "Saya mogok, silahkan /start dulu.",
                    "Saya mogok, biasanya sih habis mati lampu belum di /start lagi.",
                    "Saya mogok, /start nya dipencet dulu dong.",
                    "lagi maintenance dulu, pencet /start ya"],
                "en":  ["I cant run, please /start"]
            },

            "sholat_footnote":   {
                "id":  [
                    "Berwudhu di jam sekarang, selain seger, juga bikin hati dan pikiran lebih tenang pak.",
                    "Dengan sholat tepat waktu, semoga doa kita juga semakin cepat di dengar olehNya",
                    "Alhamdulillah masih diberi kesempatan untuk beribadah, sholat yuk",
                    "Mari tinggalkan duniawi sesaat, untuk masa depan kita di akhirat.",
                    "Istirahat dulu pak, ambil air wudhu",
                    "Sholat itu gak nyita waktu kok, cuma sebentar doang",
                    "Jangan sampai Allah berpaling sama kita karena waktu sholat aja kita gak peduli",
                    "Jangan mau ikuti bisikan setan untuk ngulur2 waktu sholat pak",
                    "'Ya Rasulullah, amalan apa yang paling utama?'\n'Shalat tepat pada waktunya'\n(HR.Bukhari)",
                    "Jagalah sholatmu, ketika ketika kau kehilangannya, kau akan kehilangan yang lainnya\n(Umar bin Khattab)",
                    "Ketahuilah, hanya dengan mengingat Allah, hati akan menjadi tentram\n(Ar-Ra'd ayat:28)",
                    "Kalau hidupmu tidak jadikan sholat sebagai penghapus dosa, maka dosa akan menghapus sholat dalam hidupmu",
                    "Yuk benahi sholat wajib, dan amalkan sholat sunnah",
                    "'dan tiadalah kehidupan di dunia ini, kecuali permainan dan kesenangan belaka.'\n(Al An'Am:32)",
                    "Perbaikilah sholatmu. Amalan yang lain akan menjadi baik\n(HR.Ath-Thabarani)",
                    "Ya Allah, sesungguhnya aku mohon kepadaMu husnul khotimah",
                    "Ya Allah, berilah hamba rezeki berupa taubat nasuhah sebelum mati",
                    "Ya Allah, yang Maha membulak-balikkan hati, tetapkanlah hatiku di atas agamaMu",
                    "Barangsiapa bertakwa kepada Allah, niscaya Dia akan mengadakan baginya jalan keluar, dan memberinya rizki dari arah yang tidak disangka-sangkanya\n(QS Ath-Thalaq:2-3)",
                    "Setiap anak Adam bersalah. Dan sebaik-baiknya orang yang bersalah adalah orang-orang yang bertaubat",
                    "Orang yang ikhlas itu seperti orang yang berjalan di atas pasir. Kita tidak mendengar suaranya, namun melihat bekasnya.\n(Ibnu Mas'ud)"
                    ],
                "en":  [
                    "Don't wait for six strong men to take you to the mosque",                    
                    "Worries end when sholat begins",
                    "Ya Allah, I am lost. Bring me back to You",
                    "Alhamdulillah for everything that happens to me, happy or sad",
                    "Do not fear, I am with you, I hear and I See \n-Allah",
                    "Do not lose hope, nor be sad\n(Quran 3:139)"
                    ]
            },

            "cmd_start":   {
                "id":  ["Saya siap menghitung\npake /set <detik> <pesan> untuk timer"],
                "en":  ["Ready to count\nuse /set <second> <message> for timer"]
            },

            "cmd_help":   {
                "id":  ["/set <detik> <pesan> untuk timer\n/set sholat <kota> untuk set jadwal sholat\n/agenda untuk liat timer yang belum dieksekusi\n\ns atau d = untuk detik\nm = untuk menit\nh atau j = untuk jam"],
                "en":  ["/set <second> <message> for timer\n/set sholat <city> for set the schedule of prayers\n/agenda to see current timer\n\ns or d = for second\nm = for minute\nh or j = for hour"]
            },

            "cmd_error":   {
                "id":  ["perintah: /set <detik> <pesan>"],
                "en":  ["command: /set <second> <message>"]
            },

            "cmd_salah":   {
                "id":  ["format salah. \ns atau d = untuk detik\nm = untuk menit\nh atau j = untuk jam"],
                "en":  ["Bad command. \ns or d = for second\nm = for minute\nh or j = for hour"]
            },

            "id_ketemu":   {
                "id":  ["ketemu dengan id : %s"],
                "en":  ["find with id : %s"]
            },

            "kota_tidak_ketemu":   {
                "id":  ["kota tidak ketemu.\nCek daftar kota di %s "],
                "en":  ["city not found.\nPlease check your city ID at %s"]
            },

            "sholat_lewat":   {
                "id":  ["-> sudah kelewat"],
                "en":  ["-> already over"]
            },

            "sholat_jadwal":   {
                "id":  ["Jadwal sholat untuk wilayah %s\ntanggal %s\n\n%s"],
                "en":  ["prayer schedule for the region of %s\ndate %s\n\n%s"]
            },

            "sholat_sudah_setting":   {
                "id":  ["jadwal sholat wilayah %s sudah di setting per hari ini"],
                "en":  ["prayer schedule for the %s area have been set today"]
            },

            "jadwal_lewat":   {
                "id":  ["Maap. Waktu sudah kelewat, kita harus move on."],
                "en":  ["Time has passed."]
            },

            "jadwal_set":   {
                "id":  ["%s <- waktu saat ini\n%s <- Timer berhasil di set"],
                "en":  ["%s <- curent time\n%s <- timer set"]
            },

            "jadwal_kosong":   {
                "id":  ["Anda tidak memiliki agenda timer"],
                "en":  ["you dont have an agenda timer"]
            },

            "jadwal_list":   {
                "id":  ["Agenda anda saat ini adalah :\n\n%s"],
                "en":  ["Your current agenda :\n\n%s"]
            },

            "sholat_teks":   {
                "id":  ["saatnya %s %s untuk wilayah %s - @%s %s"],
                "en":  ["its %s %s for the %s region - @%s %s"]
            },
        }

        sekarang = datetime.datetime.now()
        hari = datetime.datetime.strftime(sekarang.date(),"%a")
        if hari == 'Sun':
            teks = random.choice(a[teks]['en'])
        else:
            teks = random.choice(a[teks]['id'])
        return teks