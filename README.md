# CogniLearn AI — Asisten Metode Belajar

Chatbot berbasis **Retrieval-Augmented Generation (RAG)** yang menjawab pertanyaan seputar metode belajar dan kesulitan pemahaman, dengan jawaban yang diambil dari 3 jurnal ilmiah bukan dari pengetahuan umum model atau internet.

## Studi Kasus

Banyak siswa/mahasiswa memakai teknik belajar yang sebenarnya kurang efektif (misalnya sekadar membaca ulang atau menandai teks), sementara teknik yang terbukti lebih ampuh (seperti active recall atau spaced practice) kurang dikenal. Chatbot ini dibuat supaya siapa pun bisa
bertanya langsung dan mendapat jawaban yang berbasis riset, bukan opini atau mitos populer soal cara belajar.

## Sumber Data

Tiga jurnal ilmiah berbentuk PDF, disimpan di `knowledge_docs/`:

1. **Improving Students' Learning With Effective Learning Techniques** — Dunlosky, Rawson, Marsh, Nathan, & Willingham (2013). Mengevaluasi 10 teknik belajar dan tingkat utilitasnya (tinggi/sedang/rendah).
2. **From Struggle to Success: The Feynman Technique's Revolutionary Impact on Slow Learners** — Adeoye (2023). Systematic Literature Review tentang penerapan Teknik Feynman pada anak lamban belajar.
3. **The Illusion of Knowing in Metacognitive Monitoring** — Avhustiuk, Pasichnyk, & Kalamazh (2018). Studi empiris (n=262 mahasiswa) tentang kesenjangan antara rasa yakin sudah paham dan pemahaman sebenarnya.


## Model yang Digunakan

- **Model chat**: `openai/gpt-oss-120b`, diakses lewat **Groq API**
  (`langchain-groq`), `temperature=0` supaya jawaban konsisten.
- **Embedding**: dimaksudkan memakai model dari `sentence-transformers`
  (lewat `langchain-huggingface`), tapi saat ini vector store ChromaDB
  belum secara eksplisit di-set memakai model tersebut sehingga jatuh ke
  embedding default bawaan ChromaDB. *(Known issue — lihat bagian
  Keterbatasan.)*
- **Vector store**: ChromaDB, lokal, disimpan di folder `chroma_db/`.

## Cara Instalasi

1. Clone/salin folder project ini, lalu masuk ke direktorinya.
2. Buat virtual environment (opsional tapi disarankan):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```
3. Install semua dependency:
   ```bash
   pip install -r requirements.txt
   ```
4. Buat file `.env` di folder yang sama berisi API key Groq:
   ```
   GROQ_API_KEY=isi_dengan_api_key_kamu
   ```
   (Dapatkan API key gratis di [console.groq.com](https://console.groq.com))
5. Pastikan folder `knowledge_docs/` berisi ketiga file PDF jurnal.

## Cara Menjalankan

**Versi antarmuka chat (disarankan):**
```bash
streamlit run app.py
```
Buka browser ke alamat yang ditampilkan (biasanya `http://localhost:8501`).

**Versi command-line (untuk uji cepat tanpa UI):**
```bash
python rag_chatbot.py
```
Ketik pertanyaan langsung di terminal, atau ketik `keluar` untuk berhenti.

> Catatan: setiap kali dijalankan, vector store dibangun ulang dari awal (`reset_collection()`), jadi tidak perlu menghapus folder `chroma_db/` secara manual antar-run.

## Estimasi Biaya

Biaya dihitung dari pemakaian Groq API untuk model `openai/gpt-oss-120b`
(harga per Agustus 2026, cek [console.groq.com/pricing](https://console.groq.com/pricing) untuk angka terbaru):

- Input: **$0,15 / 1 juta token**
- Output: **$0,60 / 1 juta token**

Perkiraan untuk satu kali tanya-jawab (konteks retrieval + pertanyaan ~1.000 token input, jawaban ~300 token output):

```
Input : 1.000 token  x $0,15 / 1.000.000  ≈ $0,00015
Output:   300 token  x $0,60 / 1.000.000  ≈ $0,00018
Total per pertanyaan ≈ $0,00033  (± Rp5)
```

Untuk 1.000 kali tanya-jawab, estimasi biaya total sekitar **$0,33** (± Rp 5.000), belum termasuk biaya embedding (lokal gratis, karena `sentence-transformers` berjalan di perangkat sendiri tanpa API berbayar).

> Catatan: Groq menyediakan **free tier** dengan batas rate/kuota tertentu. Selama pemakaian project ini masih di bawah batas tersebut (seperti pengujian dan demo skala kecil), tidak ada biaya yang dikenakan sama sekali. Estimasi di atas berlaku untuk pemakaian di luar kuota gratis / skala produksi.