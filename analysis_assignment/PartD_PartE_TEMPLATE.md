# Part D & E — Draft (disusun dari hasil diskusi)

**Catatan**: sama seperti Q7, ini draft awal dari hasil ngobrol langsung.
Baca ulang, personalisasi kalimat yang kurang terasa seperti gaya
tulisanmu sendiri, dan tambahkan detail yang mungkin belum tergali di
percakapan kita.

---

## Part D: The Road to Embodied AI — Personal Synthesis

1. **"Missing piece" menurutku**: kombinasi (b) dan sebagian (a) — reward/
   objective yang sulit didefinisikan untuk task open-ended, ditambah
   persepsi yang rapuh di luar distribusi training. Ini aku lihat sendiri
   di Capstone project kita: agent document analyst gagal di task
   "compare paper1 and paper2" bukan karena tool-nya rusak, tapi karena
   model salah paham instruksi informal ("paper1", "paper2") dan malah
   meringkas dokumen yang salah. Task-nya sendiri jelas buat manusia,
   tapi buat AI, memetakan instruksi santai ke aksi yang tepat itu
   ternyata bukan hal yang "given" — mirip kayak bikin bot WA: sistemnya
   bisa jalan mulus di skenario yang udah diantisipasi, tapi begitu user
   nulis sesuatu yang nggak terduga, sering salah paham.

2. **Riset arah frontier**: aku belum sempat riset mendalam soal
   Foundation World Models / Neurosymbolic RL / dll karena minatku lebih
   ke security daripada robotics. Arah yang lebih related ke minatku:
   riset soal **AI red-teaming** — pakai AI buat nyari celah keamanan di
   sistem AI lain (semacam "AI vs AI" di security). Ini menarik karena
   nyambung ke rencana kariernya aku di cybersecurity, sekaligus masih
   dalam ranah agentic AI yang dipelajari modul ini. *(Kalau mau bagian
   ini lebih detail dengan sumber riset asli, aku — asisten AI — bisa
   bantu cari referensinya secara terpisah.)*

3. **Prediksi 5 tahun**: aplikasi RL+Agentic AI yang paling berdampak
   menurutku bukan di robotika fisik, tapi di **automasi bisnis lewat
   messaging platform** (WA/Telegram/dll) — karena itu yang paling deket
   sama pengalamanku sendiri dan paling cepat diadopsi UMKM/bisnis kecil
   di Indonesia. Hambatan teknis yang masih tersisa: keamanan (bot yang
   gampang dieksploitasi/disalahgunakan) dan reasoning yang masih lemah
   untuk instruksi ambigu — persis dua hal yang aku alami sendiri bikin
   bot dan yang kelihatan lagi di Capstone project ini.

---

## Part E: Career Resilience in an Age of Agentic AI

1. **Audit replaceability**: dari pengalamanku selama ini pakai AI buat
   hampir semua proses coding (nulis kode, belajar syntax, debug):
   - **Nulis kode dari instruksi jelas** → AI sudah lebih cepat dariku.
   - **Debug error dengan pesan jelas** → AI sudah lebih cepat.
   - **Belajar konsep/syntax baru** → AI cukup membantu, tapi aku masih
     perlu waktu buat benar-benar paham, bukan cuma "AI bilang gini".
   - **Milih library yang tepat untuk API nggak resmi** (kayak nyari
     Baileys buat WA) → AI kasih opsi, tapi validasi mana yang beneran
     jalan masih aku yang harus coba sendiri.
   - **Mendesain bot yang aman dari serangan** → ini yang paling jelas
     AI belum bisa gantiin — bahkan project kita sendiri butuh
     eksperimen manual buat nemuin celah (safety test di Lab 5.3).

2. **Skenario vibe-coding trap**: aku sadar sendiri kebiasaanku selama
   ini — kalau AI kasih kode, aku "langsung pakai biasanya, kadang ngecek
   kalau ada yang nggak cocok". Ini persis pola yang berbahaya kalau
   diterapkan ke bot production: waktu kita develop agent Capstone
   bareng, ada bug nyata di mana `_summarize_document` malah balikin
   JSON tool-call aneh alih-alih ringkasan teks — kalau itu nggak
   ketahuan (karena nggak dicek outputnya, cuma diasumsikan "harusnya
   jalan"), bot yang dipakai user beneran bisa ngasih respons rusak tanpa
   siapa pun sadar sampai user komplain. Skill yang mencegah ini:
   kebiasaan **selalu run & baca output actual**, bukan cuma percaya kode
   "kelihatannya benar" — persis yang akhirnya kita lakukan tiap kali
   nemu bug di sesi ini.

3. **Rencana 6 bulan**: dari 6-layer stack modul (data, simulasi, RL
   policy, LLM planner, agent loop, guardrails) — yang paling aku kuasai
   sekarang cuma **agent loop** (dari pengalaman bikin bot + project Lab
   5.3/Capstone). Yang paling lemah: **guardrails** formal (aku selama
   ini cuma coba-coba, belum belajar prinsip keamanannya secara
   terstruktur). Rencana: 2 bulan pertama coba picoCTF buat dasar
   security, 2 bulan berikutnya pelajari OWASP Top 10 khusus buat API/
   webhook security, 2 bulan terakhir coba terapkan itu buat audit ulang
   bot WA/Telegram yang udah pernah aku bikin.

4. **Hardware literacy**: masih minim — pengalamanku murni software
   (bot, API, backend). Kalau ke depan mau serius di cybersecurity, yang
   perlu diasah: dasar jaringan (bukan cuma software networking, tapi
   juga cara kerja hardware router/firewall), dan mungkin dasar reverse
   engineering hardware kalau nanti masuk ke IoT security.

5. **Skenario akuntabilitas**: kalau bot WA "AI auto service" yang aku
   bikin dipakai bisnis nyata dan AI-nya salah kasih informasi ke
   customer (misal soal harga/kebijakan refund), yang tanggung jawab
   secara hukum/reputasi adalah aku sebagai developer-nya, bukan model
   AI yang aku pakai. Keputusan desain yang bisa aku ambil: selalu ada
   *fallback ke manusia* untuk topik sensitif (harga, komplain, refund),
   dan log semua percakapan bot supaya ada jejak audit kalau ada masalah
   — mirip prinsip guardrail yang kita bahas di Part C (`analysis_
   assignment/PartC_Agentic_Risk.md`).
