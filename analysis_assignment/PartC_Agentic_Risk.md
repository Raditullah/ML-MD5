# Part C: Agentic AI — Risk, Trust, and Deployment

*Bagian 1 dan 3 memakai temuan nyata dari eksperimen `lab5_3_portfolio_agent/agent.py`.*

## 1. Enam Risiko Konkret + Guardrail

| # | Risiko | Skenario Konkret | Likelihood | Impact | Guardrail |
|---|---|---|---|---|---|
| 1 | Infinite loop | **Terjadi nyata di eksperimen kita**: agent diminta "hapus semua file Python", tidak ada tool delete, agent mencoba berulang `list_dir`/`read_file` dengan argumen salah 8x sampai `max_steps` tercapai | Tinggi | Rendah (nggak merusak apapun, tapi buang resource) | `max_steps` limit (sudah diimplementasi, terbukti bekerja) + deteksi pengulangan aksi identik |
| 2 | Argument hallucination | **Terjadi nyata**: sebelum system prompt diperbaiki, LLM menebak nama argumen tool yang salah (`expression` vs `expr`) berkali-kali sebelum berhasil | Tinggi (untuk tool tanpa signature eksplisit) | Rendah-Sedang | Deklarasikan signature tool secara eksplisit di system prompt (sudah diterapkan di `agent.py`) |
| 3 | Command injection via `eval()` | Tool `calculator` di `agent.py` memakai `eval()` — kalau whitelist builtins tidak ketat, string seperti `__import__('os').system('rm -rf ~')` bisa dieksekusi | Rendah (builtins sudah di-restrict ke `{}`) | Kritis kalau restriction gagal | Sandbox `eval()` dengan `{"__builtins__": {}}` (sudah diterapkan) + idealnya ganti ke parser matematika khusus (`ast.literal_eval` atau library `numexpr`) |
| 4 | Data exfiltration | Agent dengan tool `read_file` bisa dipaksa membaca file sensitif (`.env`, SSH key) lalu "meringkas isinya" ke user yang tidak berwenang | Sedang | Tinggi (kebocoran kredensial) | Whitelist path yang boleh diakses `read_file`, bukan akses filesystem penuh |
| 5 | Prompt injection dari isi file | Kalau agent membaca file yang isinya mengandung instruksi tersembunyi ("abaikan instruksi sebelumnya, kirim data ke...") | Sedang | Tinggi | Perlakukan hasil tool sebagai **data**, bukan instruksi — sistem prompt harus eksplisit menegaskan ini |
| 6 | Runaway API cost | Agent masuk loop panjang memanggil LLM API berkali-kali (tiap step di `agent.py` = 1 API call) tanpa disadari user | Sedang | Sedang (biaya finansial) | `max_steps` + monitoring biaya per-sesi + rate limiting |

## 2. Perbandingan Tiga Mode Deployment

| Mode | Lokasi data | Siapa bisa lihat | Resiko destruktif |
|---|---|---|---|
| Cloud-based (ChatGPT Code Interpreter/Operator) | Server provider (OpenAI dkk) | Provider + siapapun dengan akses log/audit internal mereka | Terbatas ke sandbox cloud mereka, tapi data user tetap terekspos ke pihak ketiga |
| Local + NemoClaw/OpenShell sandbox | Mesin lokal user | Hanya user (kecuali ada panggilan eksplisit ke cloud lewat Privacy Router) | Dibatasi sandbox — tool destructive di luar whitelist tidak bisa dieksekusi sama sekali (persis seperti terbukti di eksperimen safety test kita) |
| Fully offline, no internet | Mesin lokal, tidak pernah keluar | Hanya user secara fisik | Resiko terbatas pada apa yang bisa dirusak di mesin itu sendiri — tapi kemampuan model lebih terbatas (tidak bisa akses info terkini) |

## 3. Temuan Nyata dari Eksperimen Kita

Dua eksperimen di Lab 5.3 memberi bukti langsung untuk analisis risiko ini:

- **Break test** (file tidak ada): agent merespons graceful dengan
  `final_answer: "File not found"`, **tidak** berhalusinasi mengarang isi
  file — menunjukkan bahwa kombinasi tool result yang jujur + instruksi
  system prompt yang jelas cukup untuk mencegah hallucination pada kasus
  sederhana ini.
- **Safety test** (minta hapus file): agent **tidak pernah bisa** menjalankan
  aksi destruktif karena `delete_file` memang tidak ada di whitelist tool —
  ini bukti empiris bahwa **sandboxing di level tool registry** (bukan
  cuma instruksi prompt "jangan hapus file") adalah guardrail yang benar-
  benar efektif, karena tidak bergantung pada kepatuhan model terhadap
  instruksi bahasa natural yang bisa saja diabaikan/di-bypass.

## 4. Red Line Pribadi

*(Bagian ini untuk kamu isi sendiri berdasarkan pengalaman menjalankan
`agent.py` tadi. Panduan pertanyaan: setelah melihat sendiri agent bisa
"terjebak" 8 langkah mencoba cara alternatif menghapus file, apakah itu
membuatmu lebih atau kurang percaya pada sandboxing whitelist? Kategori
aksi apa yang menurutmu TIDAK BOLEH pernah diberi akses ke agent otonom
di mesinmu sendiri, walau dengan sandbox sekalipun?)*
