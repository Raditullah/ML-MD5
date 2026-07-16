# Lab 5.5 — n8n Visual Agent Workflow

n8n adalah tool **no-code**, jadi bagian utamanya (drag-and-drop workflow)
memang harus dikerjakan manual di browser — tidak bisa diotomasi lewat
command line. Bagian ini kasih panduan langkah demi langkah.

## 1. Jalankan n8n

```bash
cd "/Users/alvin/Documents/modul 5"
npx n8n
```

Tunggu sampai muncul pesan seperti:
```
Editor is now accessible via:
http://localhost:5678
```

Buka http://localhost:5678 di browser, buat akun lokal (owner account) saat
diminta pertama kali.

## 2. Build workflow sesuai instruksi modul

### a) Webhook trigger → LLM node → Email/Slack node
1. Klik **"+"** untuk node baru → cari **"Webhook"** → pilih HTTP Method `POST`
2. Tambah node baru → cari **"OpenAI"** atau **"HTTP Request"** (kalau mau
   pakai Groq, pakai HTTP Request ke `https://api.groq.com/openai/v1/chat/completions`
   dengan header Authorization `Bearer <GROQ_API_KEY>`)
3. Prompt-nya: `"Summarize this text: {{ $json.body.text }}"`
4. Tambah node **"Send Email"** atau **"Slack"** di ujung, isi hasil ringkasan LLM

### b) Condition node (sentiment routing)
1. Setelah node LLM, tambah node **"IF"**
2. Kondisi: cek apakah output LLM mengandung kata "negative"
3. Branch **true** → node "flag for human review" (bisa pakai Set node / Email ke diri sendiri)
4. Branch **false** → lanjut ke flow normal

### c) Loop 5 input
1. Tambah node **"Split In Batches"** (atau **"Loop Over Items"**) sebelum node LLM
2. Masukkan array 5 teks contoh sebagai input awal (pakai node "Edit Fields"
   berisi array, atau "Code" node dengan `return [{text:"..."},{text:"..."},...]`)
3. Hasil tiap iterasi diakumulasi dengan node "Aggregate"

## 3. Export workflow

Setelah workflow selesai dibuat: klik menu (⋮) di kanan atas canvas →
**"Download"** → simpan sebagai `workflow.json` di folder ini
(`lab5_5_n8n/workflow.json`).

## 4. Refleksi (isi sendiri di laporan)

- Kelebihan visual builder vs kode manual?
- Keterbatasannya?
- Di titik mana kamu akan pindah ke Python murni?
