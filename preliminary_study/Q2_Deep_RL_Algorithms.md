# Q2. Deep RL Algorithms — Understanding the Mechanics

## (a) DQN

**Experience Replay Buffer**: menyimpan transisi (s, a, r, s') dalam buffer
besar dan melatih network dengan mini-batch yang diambil **acak** dari buffer
ini, bukan dari urutan interaksi asli.

**Kenapa data sekuensial berbahaya?** Transisi yang berurutan dalam satu
episode sangat berkorelasi (state t+1 mirip state t). Jika neural network
dilatih langsung pada urutan ini, gradient update akan bias ke pola lokal
sesaat dan overfit ke "pengalaman terbaru", menyebabkan training tidak stabil
dan bisa berosilasi atau divergen — melanggar asumsi standar SGD bahwa sampel
training bersifat i.i.d. (independent and identically distributed).

**Target Network trick**: DQN memakai dua network — network utama Q_θ yang
di-update tiap step, dan target network Q_θ⁻ yang parameternya disalin secara
berkala (misal tiap N step). Target TD dihitung memakai Q_θ⁻, bukan Q_θ.

Ini menstabilkan training karena tanpa target network, target (r + γ·max
Q(s')) ikut berubah setiap kali Q_θ di-update — agent seperti "mengejar
target yang terus bergerak", membuat training berosilasi. Dengan target
network yang statis untuk sementara waktu, target menjadi stabil selama
periode itu.

## (b) Policy Gradient — REINFORCE

Rumus update gradient:

∇_θ J(θ) = E_π [ Σ_t ∇_θ log π_θ(a_t|s_t) · G_t ]

**Kenapa variance tinggi?** G_t adalah return Monte Carlo — dihitung dari
satu episode penuh yang dijalankan sampai selesai. Satu episode yang
kebetulan sangat beruntung/sial (misal karena stokastisitas environment)
menghasilkan G_t yang jauh dari rata-rata sebenarnya, sehingga estimasi
gradient jadi noisy dan butuh sangat banyak sample untuk konvergen stabil.

**Baseline**: mengurangi G_t dengan sebuah fungsi baseline b(s) (biasanya
estimasi nilai state V(s)), menjadi (G_t - b(s)). Ini mengurangi variance
karena baseline tidak bergantung pada aksi yang diambil — secara matematis,
E[∇_θ log π_θ(a|s) · b(s)] = 0, sehingga menambahkan/mengurangi baseline
tidak mengubah nilai ekspektasi gradient (bias tetap nol), hanya mengurangi
variance dari estimatornya.

## (c) Actor–Critic

```
        State s_t
           │
     ┌─────┴─────┐
     ▼           ▼
  Actor π_θ   Critic V_φ
  (pilih a_t) (nilai s_t)
     │           │
     ▼           ▼
  action a_t   Advantage Â_t = r_t + γV_φ(s_t+1) - V_φ(s_t)
                    │
                    ▼
          update θ (actor) & φ (critic)
```

**Advantage function A(s,a) = Q(s,a) − V(s)**: mengukur seberapa jauh lebih
baik (atau buruk) mengambil aksi spesifik a dibanding rata-rata semua aksi
yang mungkin di state s. Nilai positif berarti aksi tersebut lebih baik dari
ekspektasi rata-rata; nilai negatif berarti lebih buruk. Ini memberi sinyal
belajar yang lebih presisi dibanding Q(s,a) mentah, karena sudah
"dinormalisasi" terhadap baseline nilai state.

## (d) PPO — Clipped Surrogate Objective

Secara sederhana: PPO membatasi seberapa jauh kebijakan baru boleh berubah
dari kebijakan lama dalam satu update. Rasio r_t(θ) = π_θ(a|s) / π_θ_old(a|s)
menunjukkan seberapa besar perubahan probabilitas memilih aksi tertentu.
Objective di-"clip" ke rentang [1-ε, 1+ε] (biasanya ε=0.2), sehingga update
yang mencoba mengubah kebijakan terlalu drastis dalam satu langkah akan
dipotong pengaruhnya.

**Kenapa ini menstabilkan training?** Tanpa batasan, satu update gradient
besar bisa mendorong kebijakan ke wilayah parameter yang buruk secara
drastis — dan karena data training berikutnya dikumpulkan dari kebijakan yang
sudah rusak ini, agent sulit pulih (kebijakan buruk menghasilkan data buruk,
menghasilkan update yang makin buruk). Clipping bertindak sebagai "trust
region" praktis yang mencegah lompatan ekstrem ini tanpa perlu komputasi
rumit seperti TRPO.

## (e) SAC — Maximum Entropy RL

**Maksimalkan entropy alongside reward**: SAC tidak hanya memaksimalkan
reward kumulatif, tapi juga entropy dari kebijakan H(π(·|s)) — ukuran
"keacakan" distribusi aksi. Objective: J(π) = E[Σ r_t + α·H(π(·|s_t))].

**Kenapa ini mendorong eksplorasi tanpa ε-greedy?** Karena entropy tinggi
berarti kebijakan tetap mempertahankan probabilitas cukup besar pada
berbagai aksi, bukan langsung collapse ke satu aksi "terbaik" yang
diketahui. Ini eksplorasi yang terintegrasi langsung ke dalam objective
optimasi, bukan mekanisme eksternal seperti noise acak (ε-greedy).

**Kenapa cocok untuk continuous control/robotika?** SAC didesain untuk
action space kontinu (torsi motor, kecepatan sudut) di mana ε-greedy sulit
diterapkan langsung (aksi acak di ruang kontinu tidak terarah). Sifat
off-policy SAC juga membuatnya sample-efficient — penting untuk robotika
nyata di mana setiap interaksi fisik mahal/lambat.

## (f) Tabel Perbandingan DQN vs PPO vs SAC

| Kriteria | DQN | PPO | SAC |
|---|---|---|---|
| Action space | Diskrit saja | Diskrit & kontinu | Kontinu saja |
| On/Off-policy | Off-policy | On-policy | Off-policy |
| Sample efficiency | Sedang | Sedang | Tinggi |
| Use case rekomendasi | Atari, CartPole | General-purpose, RLHF | Robotika, kontrol kontinu |
