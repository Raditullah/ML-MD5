# Capstone Track B — Autonomous Document Analyst

Sistem agentic AI yang mengintegrasikan komponen dari seluruh 5 modul
praktikum ML, mengikuti spesifikasi Capstone Project modul 5.

## Arsitektur

```
Dokumen (.txt)
     │
     ▼
┌─────────────────────┐
│ M2: Document Loader  │  load_documents() — chunking per paragraf
│ (retrieval.py)       │
└──────────┬───────────┘
           ▼
┌─────────────────────┐
│ M3: Semantic Encoder │  sentence-transformers (MiniLM)
│ (retrieval.py)       │  embedding dokumen + query, cosine similarity
└──────────┬───────────┘
           ▼
┌─────────────────────┐
│ M4: RAG Generation   │  Groq LLM (llama-3.1-8b-instant)
│ (agent.py)           │  summarize_document, compare_documents
└──────────┬───────────┘
           ▼
┌─────────────────────┐
│ M5: Agentic Loop     │  Plan→Act→Observe→Reflect
│ (agent.py)           │  tool whitelist: search/summarize/compare/list
└──────────┬───────────┘
           ▼
      Jawaban ke user

┌─────────────────────┐
│ M1: CNN Classifier   │  ResNet18 transfer learning (terpisah, untuk
│ (document_classifier │  routing: klasifikasi halaman text-heavy vs
│  .py)                │  chart-heavy sebelum dipilih pipeline ekstraksi)
└──────────────────────┘
```

## Pemetaan ke Module 1-5

| Modul | Komponen | File | Bukti kerja |
|---|---|---|---|
| M1 | CNN transfer learning | `document_classifier.py` | ResNet18 frozen backbone + trainable head, val_acc 50%→100% dalam 5 epoch, test 6/6 benar |
| M2 | Deteksi/segmentasi konten | `retrieval.py::load_documents` | Chunking dokumen jadi blok teks (analog ke layout/region detection) |
| M3 | Transformer/language understanding | `retrieval.py::build_index, search` | Sentence-transformers MiniLM, embedding + cosine similarity search — terbukti relevan (query AgentFlow → top-3 hasil semua dari paper AgentFlow, similarity 0.70-0.73) |
| M4 | Generative AI | `agent.py::_plain_llm_call` | RAG: konteks di-retrieve lalu di-generate jadi jawaban natural via Groq LLM |
| M5 | Agentic loop | `agent.py::run_agent` | Plan→Act→Observe→Reflect, whitelist 4 tool, robust terhadap rate-limit (exponential backoff) dan JSON parsing yang berantakan |

## Cara Menjalankan

```bash
cd "/Users/alvin/Documents/modul 5"
source venv/bin/activate
export GROQ_API_KEY=your_key_here

# Test M1 (CNN classifier) secara terpisah
cd capstone_document_analyst
python document_classifier.py

# Test M3 (semantic retrieval) secara terpisah
python retrieval.py

# Jalankan sistem penuh (M2+M3+M4+M5 terintegrasi)
python agent.py
```

## Bug yang Ditemukan & Diperbaiki Selama Development

Ini bagian penting untuk laporan Capstone (Section "Discussion: what worked,
what failed"):

1. **`top_k` dikirim sebagai string oleh LLM** ("3" bukan 3) → `TypeError`
   di slicing numpy. Diperbaiki dengan `int(top_k)` eksplisit di
   `_search_documents`.
2. **LLM kadang mengeluarkan lebih dari satu JSON object per respons**
   (melanggar instruksi "ONLY JSON") → parsing gagal, membuang langkah.
   Diperbaiki dengan `json.JSONDecoder().raw_decode()` yang hanya mengambil
   blok JSON pertama, mengabaikan teks/JSON tambahan setelahnya.
3. **LLM menghalusinasi nama file** ("paper1.txt" alih-alih
   "paper1_long_horizon_rl.txt") meski nama asli sudah diberikan di hasil
   `list_documents`. Diperbaiki dengan instruksi eksplisit di system prompt:
   "use filenames EXACTLY as returned, never guess or shorten."
4. **Reuse fungsi `call_llm` dari Lab 5.3 secara naif merusak output** —
   fungsi itu selalu menyisipkan system prompt tool-calling Lab 5.3, jadi
   ketika dipakai untuk `summarize_document`/`compare_documents` (yang
   butuh teks bebas), LLM malah membalas JSON tool-call. Diperbaiki dengan
   membuat `_plain_llm_call` terpisah tanpa system prompt tool-calling.
5. **HTTP 429 (rate limit) dari Groq free tier** saat testing beruntun.
   Awalnya cuma ditambah backoff antar-retry, tapi masih gagal karena satu
   task bisa memicu 4-6 panggilan LLM beruntun (tiap step agent + tool
   seperti `summarize_document` yang juga memanggil LLM sendiri) tanpa
   jeda sama sekali. Diperbaiki dua lapis: (a) `min_interval` — jeda
   minimum 2 detik dipaksakan di **setiap** panggilan `_groq_chat`,
   ditempatkan di titik paling dasar supaya otomatis melindungi semua
   caller termasuk pemanggilan dari dalam tool; (b) exponential backoff
   tetap ada sebagai lapis kedua kalau throttling dasar belum cukup.

Bug #1-4 adalah *logic bug* murni (ditemukan lewat testing nyata, bukan
dugaan). Bug #5 adalah *infrastructure/operational* issue — keduanya
relevan dengan pembahasan "Failure Modes of Agentic AI" (Section 12 modul)
dan `analysis_assignment/PartC_Agentic_Risk.md`. Ini juga demonstrasi
langsung prinsip **"throttle di titik pusat, bukan di tiap call site"**
— pelajaran arsitektur nyata dari proses debugging ini.

## Hasil Test End-to-End (4 task)

| # | Task | Hasil |
|---|---|---|
| 1 | "What documents are available?" | ✅ Berhasil — jawaban final benar |
| 2 | "How does AgentFlow's planner differ from static prompt engineering?" | ✅ Berhasil — jawaban final benar, menggabungkan info dari 2 dokumen |
| 3 | "Compare paper1 and paper2, tell me their key difference." | ❌ Gagal — model (llama-3.1-8b-instant) salah paham dan meringkas laporan Klarna, bukan membandingkan paper1/paper2. Mencapai `max_steps` tanpa `final_answer`. |
| 4 | "Summarize the Klarna case study report in bullet points." | ✅ Berhasil — jawaban final benar, pulih dari rate-limit retry di tengah jalan |

**Analisis kegagalan task 3**: ini bukan bug kode (semua tool bekerja
benar sepanjang trace), melainkan **keterbatasan reasoning model kecil**
(8B parameter) dalam memetakan instruksi "paper1 and paper2" ke nama file
`compare_documents` yang tepat. Model malah memanggil `summarize_document`
pada dokumen yang salah. Ini contoh nyata dari materi Section 12 modul
("Failure Modes of Agentic AI") — spesifiknya mendekati kategori
*hallucination* pada level pemilihan aksi, bukan pada level fakta. Poin
penting: sistem **tidak** menghasilkan jawaban salah yang meyakinkan
(reward hacking terselubung) — sistem justru gagal transparan
(`max_steps reached`), yang jauh lebih aman daripada gagal diam-diam.
Mitigasi yang bisa dicoba: model lebih besar (llama-3.1-70b), atau
menambah contoh few-shot di system prompt untuk task perbandingan.

## Ablation Study (untuk laporan Capstone, Section "Experiments")

Coba jalankan agent tanpa komponen M3 (retrieval) — ganti `search_documents`
agar mengembalikan seluruh isi semua dokumen tanpa filtering semantik.
Bandingkan: (a) akurasi jawaban, (b) jumlah token yang dikirim ke LLM
(biaya), (c) apakah LLM tetap bisa membedakan dokumen mana yang relevan
tanpa bantuan ranking similarity.
