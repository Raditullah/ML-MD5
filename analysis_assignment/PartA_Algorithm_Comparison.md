# Part A: Deep RL Algorithm Comparison

*Berdasarkan hasil eksperimen nyata dari `lab5_1_classic_control/train.py`.*

## 1-2. Learning Curves & Analisis

Hasil evaluasi 10 episode setelah training 50,000 timesteps di CartPole-v1:

| Algoritma | Mean Reward | Std Dev |
|---|---|---|
| DQN | 377.9 | ±23.0 |
| PPO | 500.0 | ±0.0 |

Grafik: `lab5_1_classic_control/dqn_vs_ppo.png`

**PPO konvergen lebih cepat dan lebih stabil** dalam eksperimen ini — mencapai
reward maksimum sempurna (500, batas atas CartPole-v1) dengan variance nol
di seluruh 10 episode evaluasi. DQN mencapai performa lebih rendah (377.9)
dengan variance yang jauh lebih tinggi (±23.0), menandakan kebijakan yang
belum sepenuhnya konvergen dalam budget 50K timesteps yang sama.

## 3. Kenapa Ini Terjadi — Analisis Algoritmik

- **On-policy (PPO) vs off-policy (DQN)**: PPO mengumpulkan dan langsung
  memakai data dari kebijakan saat ini, dievaluasi dengan clipped surrogate
  objective yang menjaga update tetap dalam "trust region" — training jadi
  konsisten stabil. DQN off-policy bergantung pada replay buffer yang berisi
  campuran pengalaman dari kebijakan lama dan baru; efektif untuk sample
  efficiency, tapi lebih rentan terhadap estimasi Q-value yang bias/noisy
  terutama di awal training.
- **Mekanisme replay buffer**: DQN butuh replay buffer terisi cukup sebelum
  training efektif dimulai — ini "waktu pemanasan" yang mengurangi jumlah
  langkah efektif untuk belajar dibanding budget total 50K timesteps.
- **Clipped objective**: PPO secara eksplisit mencegah update kebijakan yang
  terlalu drastis dalam satu langkah — inilah kenapa hasil PPO jauh lebih
  konsisten (variance nol) dibanding DQN yang tidak punya mekanisme serupa.

## 4. Eksperimen Gamma (γ = 0.9 vs γ = 0.99)

Grafik: `lab5_1_classic_control/gamma_ablation.png`

γ = 0.9 membuat agent lebih "short-sighted" — reward 10 langkah ke depan
sudah didiskon signifikan (0.9^10 ≈ 0.35 dari nilai aslinya), sehingga agent
kurang termotivasi menjaga pole tetap seimbang untuk horizon panjang. γ =
0.99 mempertahankan hampir seluruh nilai reward jangka panjang (0.99^10 ≈
0.90), mendorong strategi yang benar-benar mengoptimalkan durasi episode
penuh — perilaku yang secara langsung selaras dengan tujuan CartPole
(bertahan selumbung mungkin).

## 5. Eksperimen Eksplorasi (ε_end = 0.01 vs 0.1)

*Dijalankan lewat `lab5_1_classic_control/epsilon_ablation.py`.*

| ε_end | Mean Reward | Std Dev |
|---|---|---|
| 0.01 (hampir selalu greedy) | 344.5 | ±94.0 |
| 0.10 (eksplorasi lebih permanen) | 500.0 | ±0.0 |

Grafik: `lab5_1_classic_control/epsilon_ablation.png`

**Hasil ini berlawanan dengan intuisi naif** ("greedy = optimal karena
selalu pilih aksi terbaik yang diketahui"). Justru ε_end=0.1 — yang tetap
mempertahankan 10% aksi acak bahkan setelah training selesai — menghasilkan
performa sempurna dan konsisten, sementara ε_end=0.01 menghasilkan performa
lebih rendah **dan** variance jauh lebih tinggi (±94.0).

**Penjelasan**: Q-value estimation di DQN tidak pernah sempurna akurat.
Kalau ε terlalu kecil, agent terlalu cepat "mengunci" pada kebijakan yang
tampak terbaik berdasarkan estimasi Q-value yang mungkin masih bias/belum
matang — sehingga rentan terjebak di kebijakan sub-optimal tanpa cukup
kesempatan mengoreksi diri lewat eksplorasi lanjutan. ε_end lebih tinggi
memberi "jaring pengaman" berkelanjutan yang mencegah overfitting dini pada
estimasi Q-value yang belum sepenuhnya konvergen, dengan konsekuensi variance
performa yang justru lebih rendah dalam kasus ini.

## 6. Refleksi — Pilihan Algoritma untuk Robotic Manipulation

*(Bagian ini opini teknis yang bisa kamu kembangkan sendiri berdasarkan data
di atas. Panduan: robotic manipulation biasanya punya action space kontinu
[posisi sendi, torsi] — DQN otomatis tereliminasi karena hanya mendukung
aksi diskrit. Pilihan realistis ada di antara PPO (stabil, general-purpose,
tapi kurang sample-efficient) vs SAC (sample-efficient, cocok kontrol
kontinu, tapi butuh tuning entropy coefficient lebih hati-hati). Faktor
penentu: berapa mahal satu interaksi nyata dengan robot fisik? Kalau sangat
mahal, sample efficiency SAC jadi prioritas.)*
