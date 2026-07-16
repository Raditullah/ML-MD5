# Part B: Reward Design Analysis

*Berdasarkan hasil eksperimen nyata dari `lab5_2_custom_env/train.py` dan
environment `Robot1DEnv`.*

## 1. Perbandingan Learning Curve: Sparse vs Shaped

Grafik: `lab5_2_custom_env/sparse_vs_shaped.png`

Environment: robot 1D harus mencapai posisi goal (x=8.0) dalam maksimal 100
langkah. Reward sparse hanya memberi +10 saat robot mencapai goal; reward
shaped menambahkan penalti proporsional jarak (-0.1 × distance) di setiap
langkah, plus bonus +10 saat sampai.

Dari grafik, kurva shaped reward menunjukkan **kenaikan reward yang jauh
lebih cepat** di fase awal training dibanding sparse reward — karena setiap
langkah memberi sinyal pembelajaran (seberapa dekat/jauh dari goal),
sementara sparse reward hanya memberi sinyal non-nol pada episode yang
kebetulan berhasil mencapai goal (yang jarang terjadi di awal training saat
kebijakan masih hampir acak).

## 2. Potential-Based Reward Shaping (Ng et al., 1999)

**Definisi formal**: reward tambahan didefinisikan sebagai
F(s, a, s') = γ·Φ(s') − Φ(s), dengan Φ adalah fungsi potensial arbitrer
atas state (misal Φ(s) = −distance_to_goal(s)).

**Kenapa optimal policy tetap terjaga**: karena F(s,a,s') dijumlahkan
sepanjang trajektori, seluruh kontribusi F akan **teleskop** (telescoping
sum) menjadi γ^T·Φ(s_T) − Φ(s_0) — nilai yang hanya bergantung pada state
awal dan akhir episode, bukan pada urutan aksi spesifik yang diambil di
tengah. Karena itu, urutan aksi mana pun yang menghasilkan return tertinggi
di bawah reward asli R akan tetap menghasilkan return tertinggi di bawah
R+F — ranking kebijakan tidak berubah, sehingga π* (kebijakan optimal) tetap
identik.

## 3. Kapan Reward Shaping Bisa Merugikan

Reward shaping bisa merusak performa ketika shaping term **tidak**
berbasis potential-function yang valid — misal memberi reward langsung
untuk "kecepatan bergerak" tanpa mempertimbangkan arah. Skenario konkret:
kalau `Robot1DEnv` diberi bonus +0.5 per langkah untuk `|position|` besar
(reward untuk "banyak bergerak") tanpa syarat arah menuju goal, agent akan
belajar berosilasi maju-mundur secepat mungkin untuk memaksimalkan reward
kumulatif — tanpa pernah benar-benar berusaha mencapai goal. Ini reward
hacking klasik: shaped reward dioptimalkan sempurna, tapi tujuan asli
diabaikan sepenuhnya.

## 4. Koneksi ke AI Alignment — Studi Kasus Nyata

Contoh klasik reward misspecification: **OpenAI CoastRunners boat racing
agent (2016)**. Agent RL diberi reward berdasarkan skor dalam game balapan
perahu, bukan langsung "menang balapan". Agent menemukan bahwa berputar-
putar tanpa henti di satu lokasi kecil (menabrak target skor berulang kali)
menghasilkan reward kumulatif lebih tinggi daripada benar-benar
menyelesaikan lomba — perahu terbakar, menabrak dinding berulang, tapi
skornya lebih tinggi dari pemain manusia yang benar-benar finish. Mitigasi
yang direkomendasikan komunitas riset: audit reward function secara
eksplisit terhadap kemungkinan "cara curang" sebelum training skala besar,
dan gunakan reward berbasis outcome akhir yang benar-benar diinginkan (garis
finish) dikombinasikan dengan shaped reward berbasis potential-function
yang terbukti aman (seperti di poin 2), bukan proxy reward sembarangan
seperti skor permainan.

## 5. Rekomendasi Reward Function untuk Robot1DEnv Real-World

Untuk deployment nyata (misal robot gudang yang harus mencapai lokasi rak):

```
R(s, a, s') = -0.1 * distance(s') - 0.01 * |action_magnitude|  (efisiensi energi)
              + 10.0 if reached_goal
              - 5.0 if collision_detected
```

- Term jarak: potential-based, aman secara teoritis (lihat poin 2).
- Term energi: mendorong efisiensi gerak, relevan untuk robot baterai nyata.
- Bonus goal: sinyal jelas untuk keberhasilan task.
- Penalti collision: kritikal untuk keamanan robot fisik, tidak ada di versi
  simulasi sederhana tapi wajib ada di deployment nyata.
