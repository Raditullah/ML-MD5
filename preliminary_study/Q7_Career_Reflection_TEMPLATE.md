# Q7. The Future of the CS Graduate — Career Reflection

**Catatan penting**: Ini **draft awal**, disusun dari hasil ngobrol langsung
denganmu (bukan digenerate generik). Baca ulang, edit kalimat yang kurang
terasa seperti "suara kamu", dan tambahkan detail personal lain yang belum
kesebut. Dosen kemungkinan besar akan tanya balik soal isi ini — pastikan
kamu benar-benar paham dan setuju dengan tiap kalimat sebelum submit.

---

## (a) The displacement landscape

Lima task software engineering yang sudah bisa (sebagian) diotomasi AI
di 2025, berdasarkan pengalamanku sendiri memakai AI untuk hampir semua
proses coding (menulis kode, belajar syntax, debugging):

1. **Menulis boilerplate/kode dari nol berdasarkan instruksi** — *fully
   automatable sekarang*. Aku sendiri sering langsung pakai kode yang
   dikasih AI tanpa banyak modifikasi. Tapi ini cuma jalan kalau task-nya
   jelas spesifikasinya; task yang butuh keputusan desain besar masih
   perlu manusia.
2. **Debugging error yang pesannya jelas** (syntax error, missing
   import, error umum) — *fully automatable*. AI biasanya langsung tahu
   penyebabnya dari pesan error saja.
3. **Mencari & memilih library yang tepat untuk kebutuhan spesifik**
   (contoh nyata: waktu aku cari library WhatsApp API yang cocok,
   akhirnya pakai Baileys) — *partially automatable*. AI bisa kasih
   daftar opsi, tapi memutuskan mana yang benar-benar stabil/reliable
   untuk use case spesifik (misalnya API tidak resmi seperti WhatsApp
   Web) masih butuh trial-and-error manusia — persis yang aku alami
   sendiri bikin bot WA.
4. **Integrasi API pihak ketiga yang dokumentasinya tidak lengkap/tidak
   resmi** — *unlikely fully automatable dalam 5 tahun*. Ini paling
   mirip pengalamanku sendiri: integrasi Baileys/Telegraf tidak selalu
   sesuai dokumentasi, banyak edge case yang cuma ketemu lewat coba-coba
   langsung di lapangan.
5. **Dokumentasi kode sederhana (README, comment)** — *fully
   automatable*, tapi dokumentasi yang menjelaskan *keputusan arsitektur*
   (kenapa pakai pendekatan X bukan Y) masih perlu manusia yang paham
   konteks bisnis di baliknya.

## (b) What AI cannot reliably do (yet)

Aku pilih fokus ke **cybersecurity**, karena ini bidang yang paling
menarik minatku, plus 4 lainnya dari daftar modul.

1. **Cybersecurity** — threat modeling dan penetration testing butuh
   *cara berpikir seperti penyerang* (attacker psychology), bukan cuma
   menjalankan checklist. Bahkan di project kita sendiri (agent Lab 5.3),
   AI-nya sendiri gagal jadi "penyerang" yang baik — waktu diminta hapus
   file, dia cuma looping bingung, bukan mencoba cara kreatif membobol
   sandbox. Justru itu bukti: mendesain sandbox yang aman butuh orang
   yang bisa mikir "gimana cara nembus ini", dan itu masih keahlian
   manusia yang sangat spesifik.
2. **Systems design** — memilih arsitektur yang tepat butuh
   mempertimbangkan constraint dunia nyata (budget, tim, deadline) yang
   sering nggak tertulis di mana pun untuk AI pelajari.
3. **Hardware debugging** — AI nggak bisa pegang alat fisik, colokin
   logic analyzer, atau lihat langsung kondisi board yang rusak.
4. **Stakeholder communication** — jelasin trade-off teknis ke orang
   non-teknis (klien, bos) butuh baca situasi sosial yang AI belum bisa.
5. **Legal/ethical accountability** — kalau bot WA/Telegram yang aku
   bikin nanti dipakai untuk penipuan atau bocorin data user, yang
   tanggung jawab hukum adalah aku sebagai pembuatnya, bukan AI yang
   bantu nulis kodenya.

## (c) The T-shaped engineer

**Horizontal (luas)**: skill AI/automation yang sudah aku bangun —
membangun bot Telegram (pakai Telegraf/Ubot) dan bot WhatsApp berbasis
AI (auto-service, mirip agent yang kita bangun di Lab 5.3 — tool-calling,
respons otomatis, dll). Course Module 5 ini nambahin pemahaman lebih
formal soal *kenapa* agent AI bisa gagal (hallucination, rate limiting,
reasoning terbatas) yang sebelumnya cuma aku rasakan sebagai "kadang
error aneh" pas develop bot sendiri.

**Vertikal (dalam)**: **cybersecurity** — network security, threat
prevention, hal-hal seputar hacking/anti-hacking. Ini yang bikin excited
walau susah.

**Kombinasi keduanya**: bot/agent yang aku bangun (WA, Telegram) itu
justru salah satu target serangan paling umum di dunia nyata — API key
bocor, webhook tanpa autentikasi, data user tersimpan tanpa enkripsi. Aku
udah lihat sendiri di Lab 5.3 gimana pentingnya *tool whitelist* supaya
agent nggak bisa dieksploitasi jadi hal yang berbahaya. Kombinasi "bisa
bikin bot/agent" + "paham cara nyerang & amanin sistem" itu kombinasi
yang jarang — banyak orang bisa bikin bot yang jalan, tapi sedikit yang
bikin bot yang *aman* dari awal desainnya.

## (d) Skills you are not getting in this course

1. **Keamanan API/webhook untuk bot production** (rate limiting,
   autentikasi token, validasi input) — penting karena bot yang aku bikin
   selama ini kemungkinan besar masih rawan disalahgunakan kalau
   dipublikasikan skala besar. Rencana: ambil course keamanan web (OWASP
   Top 10) di platform seperti TryHackMe atau Hack The Box (ada jalur
   gratis untuk pemula).
2. **Penetration testing dasar** — biar bisa nyoba "nyerang" sistem
   sendiri sebelum orang lain nyerang duluan. Rencana: coba picoCTF
   (kompetisi CTF gratis untuk pemula, disebut juga di modul ini).
3. **Reverse engineering** — buat paham gimana malware/exploit bekerja
   dari sisi attacker. Rencana: mulai dari tutorial dasar Ghidra/IDA di
   YouTube, sambil ikut komunitas CTF lokal.

## (e) The hardware frontier

Aku belum riset mendalam soal ini karena minatku lebih ke network/software
security daripada hardware AI accelerator — tapi kalau dikaitkan dengan
cybersecurity, topik yang relevan justru **hardware security modules
(HSM)** atau chip khusus untuk enkripsi/autentikasi di edge device (mirip
NVIDIA Jetson yang dibahas modul, tapi fokusnya ke keamanan bukan
inference AI). *(Catatan: kalau mau, aku — asisten AI — bisa bantu riset
lebih dalam soal ini secara terpisah supaya bagian ini lebih lengkap.)*

## (f) Your personal manifesto

Di 2030, aku pengen jadi orang yang bisa **bikin sistem otomatis (bot,
agent AI) yang bukan cuma jalan, tapi juga aman dari serangan** — kombinasi
yang jarang ditemukan karena kebanyakan developer bot cuma fokus bikin
fitur jalan, sementara kebanyakan orang keamanan nggak ngerti cara bikin
bot/agent AI beneran. Aku udah mulai dari sisi "bisa bikin" — bot WA dan
Telegram udah pernah aku bangun sendiri, penuh trial-and-error nyari
library yang tepat kayak Baileys. Yang aku belum kuasai dan mau aku kejar
adalah sisi keamanannya: gimana caranya mikir kayak attacker, supaya aku
bisa amanin sistem yang aku bangun sendiri sebelum orang lain
mengeksploitasinya.

Yang bikin kerjaanku masih relevan nanti: AI makin canggih bikin kode,
tapi AI belum (dan mungkin nggak akan) bisa mikir kreatif kayak seorang
hacker yang niat jahat — dan justru itu yang dibutuhkan buat ngamanin
sistem AI/bot yang makin banyak dipakai orang.
