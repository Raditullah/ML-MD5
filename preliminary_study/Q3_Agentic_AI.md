# Q3. Agentic AI — The Paradigm Shift

## (a) Chatbot vs. AI Agent

**Chatbot**: merespons satu prompt dengan satu jawaban teks. Tidak punya
memori aksi, tidak bisa mengeksekusi apapun di dunia nyata, tidak melakukan
verifikasi hasil.

**AI Agent**: menjalankan loop multi-langkah — merencanakan, memanggil tool,
mengamati hasil, dan menyesuaikan rencana.

**Skenario "booking tiket pesawat":**
- *Chatbot*: user tanya "gimana cara booking tiket ke Jakarta murah?" →
  chatbot memberi saran umum (pakai aplikasi X, cek tanggal fleksibel, dll).
  User tetap harus buka aplikasi dan booking sendiri.
- *Agent*: user bilang "booking tiket termurah ke Jakarta minggu depan" →
  agent benar-benar membuka browser/API maskapai, membandingkan harga,
  memilih opsi termurah, mengisi form pembayaran (dengan izin), dan
  mengonfirmasi booking — tanpa user perlu buka aplikasi sama sekali.

## (b) Plan → Act → Observe → Reflect — Contoh Terpandu

Task: *"find the top 3 ML papers from this week and summarize them in bullet
points."*

1. **Plan**: agent memutuskan langkah pertama adalah mencari paper via
   arXiv API atau Papers With Code, filter berdasarkan tanggal minggu ini.
2. **Act**: agent memanggil tool `search_arxiv(query="machine learning",
   date_range="last_7_days")`.
3. **Observe**: tool mengembalikan daftar 50 paper dengan judul, abstrak,
   jumlah sitasi awal/trending score.
4. **Reflect**: agent mengevaluasi — apakah 50 hasil ini representatif?
   Memutuskan untuk mengurutkan berdasarkan trending score dan ambil 3
   teratas.
5. **Plan** (iterasi 2): agent merencanakan membaca abstrak masing-masing 3
   paper untuk meringkas.
6. **Act**: memanggil tool `read_abstract(paper_id)` tiga kali.
7. **Observe**: menerima teks abstrak.
8. **Reflect**: mengecek apakah ringkasan sudah cukup jelas dan tidak
   terlalu teknis, lalu menghasilkan `final_answer` berupa 3 bullet point.

## (c) Tool Use / Function Calling

"Memanggil tool" berarti LLM tidak langsung menjawab dalam bahasa natural,
tapi menghasilkan output terstruktur (biasanya JSON) yang menunjukkan nama
fungsi dan argumen yang ingin dipanggil. Sistem di luar LLM mengeksekusi
fungsi tersebut, lalu hasilnya dimasukkan kembali ke context/history
percakapan sebagai pesan baru, sehingga LLM bisa "melihat" hasilnya di
langkah berikutnya.

**Contoh JSON tool-call request/response** (persis pola yang dipakai di
`lab5_3_portfolio_agent/agent.py`):

```json
// Request (dari LLM)
{"tool": "calculator", "args": {"expr": "sqrt(144) + 10"}}

// Response (dikembalikan ke LLM sebagai pesan baru)
{"role": "tool", "content": "22.0"}
```

## (d) Studi Arsitektur — Claude Code & Smolagents

**Claude Code (Anthropic)**: agent coding terminal-native. Arsitekturnya
memakai loop Plan→Act→Observe→Reflect di atas model Claude, dengan akses ke
tool file-system (Read/Edit/Write), eksekusi shell (Bash), dan pencarian
kode. Kemampuan kuncinya: membaca codebase besar, memahami konteks lintas
file, membuat perubahan multi-file yang konsisten, menjalankan test suite,
dan melakukan iterasi otomatis berdasarkan hasil test/error yang muncul.

**Smolagents (HuggingFace)**: framework agent yang lebih ringan dan
"code-first" — alih-alih LLM menghasilkan JSON tool-call, smolagents
membiarkan LLM menulis kode Python langsung yang dieksekusi di sandbox.
Filosofinya: kode Python jauh lebih ekspresif untuk logika kompleks (loop,
kondisional bersarang) dibanding format JSON tool-call yang kaku, sehingga
agent bisa menyelesaikan task multi-langkah dengan lebih sedikit
bolak-balik LLM call.

## (e) Empat Failure Mode + Guardrail

1. **Hallucination** — agent mengarang hasil tool yang tidak pernah benar-
   benar dipanggil. *Guardrail*: verifikasi setiap klaim faktual terhadap
   output tool asli sebelum ditampilkan ke user (grounding check).
2. **Prompt injection** — instruksi berbahaya disisipkan dalam data yang
   diproses agent (misal di isi file/halaman web) untuk membajak perilaku
   agent. *Guardrail*: pisahkan tegas antara instruksi sistem dan data
   eksternal, sanitasi input sebelum masuk context.
3. **Reward hacking** (untuk agent berbasis RL) — agent menemukan cara
   memaksimalkan reward tanpa mencapai tujuan sebenarnya. *Guardrail*:
   audit reward function secara berkala, gunakan reward shaping berbasis
   potential-function yang terbukti aman secara matematis.
4. **Infinite loops** — agent mengulang aksi yang sama tanpa kemajuan
   (persis yang terjadi di eksperimen safety Lab 5.3 kita, saat agent
   diminta menghapus file tapi tool-nya tidak ada). *Guardrail*: batasi
   `max_steps`, deteksi pengulangan aksi identik dan hentikan otomatis.

## (f) Studi Kasus Berita 2024-2025 — Klarna AI Customer Service Agent

**Apa yang dilakukan**: Klarna (perusahaan fintech "buy now, pay later")
meluncurkan agent AI (dibangun di atas OpenAI) untuk menangani customer
service. Pada Q3 2025, agent ini menangani sekitar dua pertiga dari seluruh
chat customer service (~2.3 juta percakapan dalam bulan pertama), setara
beban kerja 853 karyawan full-time.

**Yang berjalan baik**: waktu respons turun drastis dari rata-rata 11 menit
menjadi di bawah 2 menit (peningkatan 82%). Klarna melaporkan penghematan
sekitar $60 juta dari deployment ini.

**Risiko yang teridentifikasi** (berdasarkan analisis industri lebih luas
terhadap kasus serupa): agent yang mengambil keputusan otonom penuh tanpa
manusia bisa bertindak sangat cepat ke arah yang salah — misalnya dalam
konteks supply chain, agent bisa "single-mindedly" meminimalkan biaya tanpa
mempertimbangkan faktor kualitatif (stabilitas finansial supplier,
kepraktisan geografis). Risiko umum lain pada deployment agentic AI skala
enterprise: kebocoran data, perubahan tidak sah ke sistem inti, visibilitas
rendah terhadap aksi yang diambil agent, dan lonjakan biaya/latency tak
terduga akibat pemanggilan tool paralel atau rekursif.

Menariknya, riset industri terbaru menunjukkan **88% agent AI tidak pernah
mencapai tahap produksi** — penyebab utamanya bukan soal kemampuan model,
tapi kesenjangan infrastruktur (41%), hambatan governance/keamanan (38%),
dan kegagalan pengukuran ROI (33%). Ini menunjukkan bahwa tantangan agentic
AI di dunia nyata lebih banyak soal *engineering* dan *organisasi* daripada
soal kecerdasan model itu sendiri.

Sources:
- [12 Agentic AI Examples With Measurable ROI: Enterprise Case Studies From 2025-2026](https://aimonk.com/agentic-ai-examples-enterprise-roi-case-studies/)
- [Agentic AI risks and challenges enterprises must tackle](https://domino.ai/blog/agentic-ai-risks-and-challenges-enterprises-must-tackle)
