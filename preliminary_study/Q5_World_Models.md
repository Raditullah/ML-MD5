# Q5. World Models — Teaching Machines to Imagine

## (a) Definisi Formal World Model

World model didefinisikan sebagai pasangan fungsi yang dipelajari:

ŝ_(t+1) = f_θ(s_t, a_t)  — memprediksi state berikutnya
r̂_(t+1) = r_θ(s_t, a_t)  — memprediksi reward berikutnya

**Kenapa dramatis meningkatkan sample efficiency?** Karena agent bisa
"membayangkan" (simulasi rollout) banyak skenario di dalam world model tanpa
perlu benar-benar berinteraksi dengan environment nyata yang mahal/lambat.
Satu interaksi nyata bisa menghasilkan ribuan "pengalaman imajiner" di
dalam model, sehingga jumlah interaksi nyata yang dibutuhkan untuk mencapai
performa tertentu jauh lebih sedikit dibanding model-free RL yang harus
belajar murni dari trial-and-error nyata.

## (b) Model-Free vs Model-Based RL

Model-free RL (PPO, DQN) belajar kebijakan/value function langsung dari
pengalaman, tanpa pernah membangun model eksplisit tentang bagaimana
environment bekerja. Model-based RL (Dreamer, MuZero) membangun model
dinamika environment terlebih dahulu, lalu memakai model itu untuk
merencanakan (planning) atau menghasilkan data training tambahan (simulasi
imajiner).

Model-based RL lebih disukai ketika: interaksi nyata sangat mahal atau
berisiko (robotika fisik, kendaraan otonom, aplikasi medis) — karena
sample efficiency-nya jauh lebih tinggi. Model-free lebih disukai ketika
simulator sudah sangat cepat dan murah (game Atari) sehingga tidak ada
insentif kuat membangun model dinamika terpisah, dan risiko "model
exploitation" (agent mengeksploitasi ketidakakuratan model, bukan
environment sebenarnya) bisa dihindari sama sekali.

## (c) Google Genie (2024)

Genie belajar dari 200,000 jam video internet game platformer 2D **tanpa
label aksi sama sekali**. Mekanismenya: video di-tokenisasi (VQ-VAE),
kemudian **latent action model (LAM)** secara unsupervised menyimpulkan
"aksi tersembunyi" apa yang mungkin menyebabkan perubahan antara satu frame
video dan frame berikutnya — tanpa pernah diberi tahu label aksi eksplisit
(seperti "tombol kiri" atau "lompat"). Model ini pada dasarnya menemukan
sendiri struktur ruang aksi hanya dari pola perubahan visual antar-frame.
Dynamics model (Transformer) kemudian dilatih memprediksi frame berikutnya
diberi frame saat ini + aksi laten yang dipilih, sehingga menghasilkan
environment interaktif yang bisa "dimainkan" hanya dari satu gambar prompt.

## (d) DreamerV3 (DeepMind)

DreamerV3 menggunakan world model berbasis **RSSM (Recurrent State-Space
Model)** yang belajar representasi laten dari observasi. Selama
**planning/training**, agent menjalankan rollout imajiner sepenuhnya di
dalam ruang laten world model (bukan di environment nyata) — dari situ
dihitung reward imajiner dan value estimate, lalu actor-critic dilatih
sepenuhnya dari pengalaman imajiner ini. Keunggulan utamanya adalah satu
set hyperparameter yang sama bekerja stabil di 150+ task berbeda tanpa
tuning ulang — sebuah pencapaian yang jarang dalam RL karena biasanya
tiap environment butuh tuning hyperparameter terpisah.

## (e) Big Picture — Refleksi

*(Bagian ini untuk kamu isi sendiri. Panduan berpikir: World models sering
disebut "missing piece" untuk robotika general-purpose. Pertimbangkan:
apakah sebuah world model yang "sempurna" harus memodelkan fisika secara
eksak, atau cukup memodelkan konsekuensi yang relevan secara statistik?
Keterbatasan yang jelas dari sistem seperti Genie/DreamerV3 saat ini:
horizon prediksi terbatas — akurasi model menurun drastis untuk prediksi
jangka sangat panjang; generalisasi ke domain sangat berbeda dari data
training masih terbatas; dan belum ada world model yang menangkap fisika
kontak/deformasi objek kompleks dengan akurat. Tulis pendapatmu sendiri
berdasarkan poin-poin ini.)*
