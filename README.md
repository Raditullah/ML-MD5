# Module 5 — Deep RL & Agentic AI

Implementasi kode + tulisan pendukung untuk materi Module 5, dikerjakan di
MacBook Pro M5 Pro (Apple Silicon, CPU-only, tanpa GPU NVIDIA).

## Environment yang dipakai (penting!)

Ada 2 environment Python terpisah di project ini karena perbedaan kebutuhan
versi Python/compiler:

| Env | Python | Dipakai untuk |
|---|---|---|
| `venv/` | 3.9 | Lab 5.1, 5.2, 5.3, 5.4, Capstone |
| `mamba_env/` | 3.11 (conda-forge) | Lab 5.6 — perlu pybullet pre-built karena compile lokal gagal di macOS SDK terbaru |

## Setup dasar

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Lab 5.1 — Classic Control (`lab5_1_classic_control/`) ✅ selesai

DQN vs PPO di CartPole-v1 + ablasi gamma. Hasil: PPO 500±0, DQN 377.9±23.

```bash
source venv/bin/activate
cd lab5_1_classic_control && python train.py
python epsilon_ablation.py   # DQN eps_end=0.01 vs 0.1
```

Epsilon ablation: ε_end=0.1 (500±0) mengalahkan ε_end=0.01 (344.5±94.0) —
lebih banyak eksplorasi permanen justru lebih baik & lebih stabil, temuan
yang berlawanan intuisi naif "greedy = optimal". Detail di
`analysis_assignment/PartA_Algorithm_Comparison.md`.

## Lab 5.2 — Custom Environment (`lab5_2_custom_env/`) ✅ selesai

`Robot1DEnv` — robot 1D custom, sparse vs shaped reward, `check_env` lolos.

```bash
source venv/bin/activate
cd lab5_2_custom_env && python train.py
```

## Lab 5.3 — Portfolio Agent (`lab5_3_portfolio_agent/`) ✅ selesai

Agent tool-calling aman (whitelist), loop Plan→Act→Observe→Reflect, pakai
Groq API. Sudah diuji: 3 task sukses, break test graceful, safety test
terbukti tidak bisa hapus file (sandboxing bekerja, tapi masuk infinite
loop sampai `max_steps` — temuan nyata, sudah didokumentasikan). Portfolio
Extension juga sudah ditambahkan: tool `git_status` dan `read_readme` —
teruji bisa navigasi repo dan meringkas README secara otomatis.

```bash
source venv/bin/activate
export GROQ_API_KEY=your_key_here   # https://console.groq.com/keys
cd lab5_3_portfolio_agent && python agent.py
```

## Lab 5.4 — TorchRL (`lab5_4_torchrl/`) ✅ selesai (opsional)

Data collector + TensorDict demo di CartPole, CPU-only.

```bash
source venv/bin/activate
cd lab5_4_torchrl && python train.py
```

## Lab 5.5 — n8n (`lab5_5_n8n/`) ⚠️ setup di background

No-code visual workflow builder. Server dijalankan di background
(`n8n_server.log`), buka http://localhost:5678 di browser. Langkah build
workflow-nya manual (drag-and-drop) — lihat `PANDUAN.md` di folder ini.

Catatan teknis: n8n punya modul native (`isolated-vm`) yang tidak
kompatibel dengan Node.js v26 (default Homebrew di mesin ini) — solusinya
pakai Node 22 LTS yang diinstall terpisah di `/opt/homebrew/opt/node@22/`.

## Lab 5.6 — Drone RL Part A (`lab5_6_drone_rl/`) ✅ selesai

`gym-pybullet-drones` HoverAviary + PPO. **Pakai `mamba_env`, bukan `venv`**
karena pybullet gagal compile dari source di macOS SDK 26 (bug kompatibilitas
`zlib`/`fdopen` di clang terbaru) — pybullet di-install lewat conda-forge
sebagai binary pre-built.

```bash
cd lab5_6_drone_rl && ../mamba_env/bin/python train_hover.py
```

Training terbukti berjalan (2023 fps, explained_variance 0.744).

## Lab 5.6 Part B & Lab 5.7 — ❌ Tidak bisa dijalankan lokal

- **Lab 5.6 Part B (AirSim/Colosseum)**: butuh Unreal Engine + GPU dedicated,
  tidak praktis di Apple Silicon.
- **Lab 5.7 (Isaac Lab/Isaac Sim)**: **wajib** NVIDIA GPU + CUDA. Ini bukan
  soal performa — Isaac Sim tidak punya build untuk macOS/ARM sama sekali.
  Satu-satunya jalan: NVIDIA Brev cloud (berbayar) atau remote ke mesin
  Windows/Linux dengan GPU NVIDIA (misal RTX 5060 lewat Remote Desktop).

## Preliminary Study Assignment (`preliminary_study/`) ⚠️ sebagian

Q1-Q6 sudah ditulis lengkap (jawaban teknis, termasuk riset paper 2025 via
web search dengan sumber). **Q7 sengaja dibiarkan sebagai template** —
soal itu murni refleksi karier personal, tidak etis digantikan tulisan AI
untuk disubmit sebagai milikmu sendiri (lihat `Q7_Career_Reflection_TEMPLATE.md`).

## Analysis Assignment (`analysis_assignment/`) ⚠️ sebagian

Part A-C sudah ditulis lengkap berdasarkan data eksperimen nyata dari Lab
5.1-5.3. **Part D-E sengaja dibiarkan sebagai template** (personal
synthesis + career resilience) — sama alasannya dengan Q7.

## Capstone Final Project (`capstone_document_analyst/`) ✅ selesai — Track B

**Autonomous Document Analyst** — mengintegrasikan M1-M5:

| Modul | Komponen | Bukti kerja nyata |
|---|---|---|
| M1 | CNN transfer learning (`document_classifier.py`) | ResNet18, val_acc 50%→100% dalam 5 epoch, test 6/6 benar |
| M2 | Document loader/chunking (`retrieval.py`) | 15 chunks dari 3 dokumen |
| M3 | Semantic search (`retrieval.py`) | sentence-transformers, query relevan → similarity 0.70-0.73 ke dokumen yang tepat |
| M4 | RAG generation (`agent.py`) | Groq LLM, jawaban grounded dari konteks retrieval |
| M5 | Agentic loop (`agent.py`) | 4 tool whitelist, throttling + exponential backoff, 3/4 task end-to-end sukses |

```bash
source venv/bin/activate
export GROQ_API_KEY=your_key_here
cd capstone_document_analyst
python document_classifier.py   # M1
python retrieval.py             # M2+M3
python agent.py                 # M2+M3+M4+M5 terintegrasi penuh
```

Detail arsitektur, bug yang ditemukan+diperbaiki selama development, dan
hasil test lengkap ada di `capstone_document_analyst/README.md` — termasuk
1 kegagalan task nyata (keterbatasan reasoning model kecil, bukan bug kode)
yang didokumentasikan sebagai temuan, bukan disembunyikan.

**Belum dikerjakan dari spesifikasi Capstone modul**: laporan tertulis
10-15 halaman lengkap (Abstract, Related Work, dst — kerangkanya sudah ada
tapi belum ditulis penuh), live demo 5 menit, dan bagian "Ethical
Considerations" formal.
# ML-MD5
