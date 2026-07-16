# Q6. The Current Frontier — Self-Directed Research

## (a) Satu Paper RL + Satu Paper Agentic AI (2024-2025)

### Paper RL: "Reinforcement Learning for Long-Horizon Interactive LLM Agents"
(arXiv:2502.01600, 2025)

- **Masalah yang diselesaikan**: melatih LLM agent untuk task interaktif
  jangka-panjang (multi-turn, butuh banyak langkah) biasanya membutuhkan
  data ground-truth action sequence yang mahal dikumpulkan, atau dataset
  training yang sangat besar.
- **Inovasi kunci**: metode bernama **LOOP** — menggabungkan PPO dengan
  estimasi baseline "leave-one-out" (baseline dihitung dari rata-rata
  return sampel-sampel lain dalam batch, bukan dari value network
  terpisah) dan clipping per-token (bukan per-episode).
- **Kenapa penting**: menunjukkan bahwa RL bisa efektif melatih agent LLM
  interaktif jangka panjang **tanpa** perlu ground-truth action sequences
  mahal atau dataset raksasa — menurunkan barrier praktis untuk melatih
  agent LLM yang benar-benar melakukan banyak langkah aksi nyata (bukan
  cuma menjawab satu prompt).

### Paper Agentic AI: "In-the-Flow Agentic System Optimization for Effective
Planning and Tool Use" (arXiv:2510.05592, 2025) — framework **AgentFlow**

- **Masalah yang diselesaikan**: kebanyakan sistem agent LLM (planner,
  tool-caller, verifier) dioptimasi secara terpisah/statis — planner tidak
  belajar dari hasil aksi yang gagal atau feedback loop yang sesungguhnya.
- **Inovasi kunci**: AgentFlow mengoordinasikan **empat modul** (planner,
  executor, verifier, generator) lewat memori yang terus berkembang
  (evolving memory), dan secara langsung mengoptimasi planner **di dalam**
  loop multi-turn itu sendiri — bukan dilatih terpisah lalu di-freeze.
- **Kenapa penting**: ini bergerak dari paradigma "agent = LLM statis +
  prompt engineering" ke "agent yang komponennya benar-benar dilatih
  end-to-end dari pengalaman multi-langkahnya sendiri" — mendekatkan
  agentic AI ke prinsip RL klasik (belajar dari konsekuensi aksi), bukan
  cuma reasoning satu-shot.

## (b) RLHF vs RLAIF vs DPO

- **RLHF (Reinforcement Learning from Human Feedback)**: melatih reward
  model dari preferensi manusia, lalu fine-tune LLM dengan RL (PPO)
  memakai reward model itu. Paling akurat merepresentasikan preferensi
  manusia sesungguhnya, tapi mahal (butuh anotator manusia) dan pipeline-nya
  kompleks (3 tahap: SFT → reward model → RL).
- **RLAIF (RL from AI Feedback)**: mengganti anotator manusia dengan LLM
  lain sebagai "judge" pemberi preferensi. Jauh lebih murah dan cepat
  discale, tapi kualitas bergantung pada kualitas AI judge — berisiko
  mewariskan bias/kelemahan judge model ke model yang dilatih.
- **DPO (Direct Preference Optimization)**: melewati tahap reward model
  dan RL loop sepenuhnya — langsung mengoptimasi kebijakan dari data
  preferensi pasangan (chosen vs rejected) memakai loss function
  closed-form yang setara secara matematis dengan RLHF di bawah asumsi
  tertentu.

**Paling praktis untuk skala besar**: **DPO**, karena jauh lebih sederhana
diimplementasi (tidak perlu reward model terpisah, tidak perlu loop RL yang
rentan tidak stabil), lebih murah secara komputasi, dan cukup banyak studi
menunjukkan hasil kompetitif dengan RLHF penuh untuk banyak use case —
meski RLHF/RLAIF penuh masih unggul untuk kasus yang butuh reward signal
sangat halus/adaptif.

## (c) Constitutional AI & Process Reward Models

**Constitutional AI (Anthropic)**: model dilatih untuk mengkritik dan
merevisi responsnya sendiri berdasarkan seperangkat prinsip eksplisit
("konstitusi") tanpa butuh label manusia untuk setiap contoh — mengurangi
ketergantungan pada anotasi manusia berskala besar untuk safety alignment.

**Process Reward Models (PRM)**: alih-alih hanya menilai hasil akhir
(outcome reward), PRM memberi reward untuk setiap **langkah** penalaran
antara — sangat relevan untuk agentic AI karena banyak kegagalan agent
terjadi di langkah tengah (memilih tool salah, salah interpretasi hasil
tool), bukan cuma di jawaban akhir.

**Relevansi untuk keamanan agentic AI**: kombinasi keduanya bisa membuat
agent yang (1) mengevaluasi dan mengoreksi rencananya sendiri terhadap
prinsip eksplisit sebelum eksekusi (Constitutional AI), dan (2) mendapat
sinyal koreksi di setiap langkah proses, bukan hanya di akhir (PRM) —
sehingga kesalahan bisa terdeteksi dan dikoreksi lebih dini sebelum agent
terlanjur mengambil aksi berisiko di dunia nyata.

## (d) Refleksi — Aplikasi Near-Term RL + Agentic AI

*(Bagian ini untuk kamu isi sendiri, 1-2 paragraf. Panduan: pikirkan
kombinasi konkret — misal agent LLM yang merencanakan task tingkat tinggi
lalu mendelegasikan eksekusi presisi ke kebijakan RL terlatih [seperti
SayCan/RT-2 yang dibahas di modul], diterapkan ke domain yang kamu minati
sendiri (robotika rumah tangga, asisten riset otomatis, automasi
industri, dst). Sebutkan SATU barrier spesifik — teknis, etis, atau
praktis — yang menurutmu paling mungkin memperlambat adopsinya.)*

---

Sources:
- [Reinforcement Learning for Long-Horizon Interactive LLM Agents](https://arxiv.org/pdf/2502.01600)
- [In-the-Flow Agentic System Optimization for Effective Planning and Tool Use](https://arxiv.org/abs/2510.05592)
