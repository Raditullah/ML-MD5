# Q1. Reinforcement Learning Foundations

## (a) Markov Decision Process (MDP)

Sebuah MDP didefinisikan sebagai tuple (S, A, P, R, γ):

- **S (State space)**: himpunan semua kondisi yang mungkin dialami agent.
- **A (Action space)**: himpunan semua aksi yang bisa diambil agent.
- **P(s'|s,a) (Transition function)**: probabilitas berpindah ke state s'
  setelah mengambil aksi a di state s.
- **R(s,a) (Reward function)**: sinyal skalar yang diterima agent setelah
  mengambil aksi a di state s.
- **γ (Discount factor)**: seberapa besar agent menghargai reward di masa depan
  (0 ≤ γ < 1).

**Contoh nyata: sistem rekomendasi lagu (music streaming)**

| Komponen | Contoh konkret |
|---|---|
| S | riwayat 10 lagu terakhir yang didengar user + waktu hari + mood inferred |
| A | {putar lagu A, putar lagu B, ..., skip} |
| P(s'\|s,a) | probabilitas user tetap mendengarkan / skip setelah lagu tertentu diputar |
| R(s,a) | +1 jika user dengar sampai selesai, -1 jika skip cepat, +5 jika like |
| γ | 0.95 — sistem lebih mengutamakan engagement jangka panjang (langganan bertahan) dibanding satu sesi saja |

## (b) Agent–Environment Loop dan Markov Property

```
        action a_t
Agent ────────────────► Environment
  ▲                          │
  │   state s_(t+1),         │
  └── reward r_(t+1) ◄───────┘
```

Di setiap timestep t: agent mengamati state s_t, memilih aksi a_t menurut
kebijakan π(a|s), environment berpindah ke s_(t+1) dan memberi reward r_(t+1).

**Kenapa Markov property wajib?** Markov property menyatakan bahwa
P(s_(t+1) | s_t, a_t) = P(s_(t+1) | s_1, a_1, ..., s_t, a_t) — state saat ini
sudah mengandung semua informasi relevan untuk memprediksi masa depan, riwayat
sebelumnya tidak menambah informasi. Kalau properti ini dilanggar (state tidak
lengkap), Bellman equation tidak valid lagi karena nilai V(s) tidak bisa
dihitung hanya dari s saja — agent butuh riwayat penuh, yang membuat seluruh
kerangka RL berbasis MDP runtuh secara teoritis.

## (c) Discounted Return

G_t = Σ(k=0 to ∞) γ^k · r_(t+k+1)

- **γ → 0**: agent sepenuhnya greedy/miopik — hanya reward langsung yang
  dihitung, reward masa depan diabaikan.
- **γ → 1**: agent sangat visioner — reward 100 langkah ke depan dihargai
  hampir sama dengan reward sekarang.

**Analogi manusia**: γ rendah seperti orang yang menghabiskan seluruh gaji
bulan ini untuk kesenangan instan (mengabaikan konsekuensi finansial masa
depan). γ tinggi seperti orang yang rutin menabung untuk dana pensiun 30
tahun lagi — rela menahan kesenangan sekarang demi hasil jangka panjang.

## (d) Exploration vs. Exploitation

Dilema ini adalah trade-off antara memanfaatkan pengetahuan yang sudah
dimiliki agent (exploitation — pilih aksi dengan Q-value tertinggi yang
diketahui) versus mencoba aksi baru yang belum banyak diuji (exploration —
untuk menemukan kemungkinan aksi yang lebih baik lagi).

| Strategi | Cara kerja | Kapan dipakai |
|---|---|---|
| ε-greedy | Dengan probabilitas ε pilih aksi acak, selain itu pilih argmax Q | Sederhana, cocok untuk baseline cepat; ε biasanya di-decay seiring training |
| Boltzmann/Softmax | Sampling aksi ∝ exp(Q(s,a)/τ) | Ketika ingin proporsionalitas — aksi dengan Q sedikit lebih rendah masih punya peluang wajar dipilih, bukan biner acak/tidak seperti ε-greedy |
| UCB | argmax [Q + c√(ln t / N(a))] — beri bonus untuk aksi yang jarang dicoba | Multi-armed bandit atau kasus dengan jumlah aksi terbatas dan butuh eksplorasi lebih terarah/principled |

## (e) Studi Kasus: AlphaGo (DeepMind)

- **State space**: konfigurasi papan Go 19×19 (~10^170 kemungkinan posisi legal)
- **Action space**: ~361 titik kosong yang bisa diisi batu di tiap giliran
- **Reward signal**: +1 jika menang, -1 jika kalah, diberikan hanya di akhir
  permainan (sparse reward)

**Tantangan mendefinisikan reward**: karena reward hanya muncul di akhir
game (menang/kalah), sulit menilai kontribusi tiap langkah individu terhadap
hasil akhir (credit assignment problem). DeepMind mengatasi ini dengan
kombinasi supervised learning dari game manusia (untuk inisialisasi
kebijakan) dan self-play reinforcement learning dengan Monte Carlo Tree
Search untuk mengevaluasi kualitas posisi menengah tanpa perlu reward
eksplisit di tiap langkah.
