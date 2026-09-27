import os
import glob
import base64

import streamlit as st
from dotenv import load_dotenv

from rag_chatbot import (
    CHAT_MODEL,
    KNOWLEDGE_DIR,
    SYSTEM_PROMPT_PATH,
    TOP_K,
    buat_model,
    muat_dokumen,
    bangun_vectorstore,
    muat_system_prompt,
    buat_rag_chain,
)

# Dipakai untuk panel "Info sistem" di sidebar.
CHAT_MODEL_LABEL = CHAT_MODEL
jumlah_dokumen_sumber = len(glob.glob(os.path.join(KNOWLEDGE_DIR, "*.pdf")))

# ============================================================
# 1. PENGATURAN HALAMAN
# ============================================================
# Wajib jadi perintah Streamlit pertama: judul tab browser dan ikonnya.

st.set_page_config(
    page_title="CogniLearn Chatbot — Asisten Metode Belajar",
    page_icon=":material/hub:",
)

# ============================================================
# 2. CEK API KEY
# ============================================================
# Di laptop, GROQ_API_KEY dibaca dari file .env.
# Di Streamlit Cloud, GROQ_API_KEY diisi lewat menu Secrets, dan Streamlit
# otomatis menjadikannya environment variable. Jadi kode yang sama ini
# jalan di dua tempat tanpa perlu diubah.

load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    st.error(
        "GROQ_API_KEY belum diisi. Cek file .env (di laptop) "
        "atau menu Secrets (di Streamlit Cloud)."
    )
    st.stop()

# ============================================================
# 3. SIAPKAN MESIN CHATBOT (sekali saja, lalu disimpan)
# ============================================================
# Streamlit menjalankan ulang SELURUH file ini dari atas setiap kali
# pengguna berinteraksi (misalnya mengirim pertanyaan).
# @st.cache_resource membuat fungsi di bawah ini cukup dijalankan SEKALI.
# Hasilnya disimpan, lalu dipakai ulang, sehingga dokumen tidak dimuat
# ulang dan vector store tidak dibangun ulang di setiap pertanyaan.

@st.cache_resource(show_spinner="Menyiapkan chatbot, mohon tunggu sebentar...")
def siapkan_chatbot():
    model = buat_model()
    dokumen = muat_dokumen(KNOWLEDGE_DIR)
    vectorstore = bangun_vectorstore(dokumen)
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    system_prompt = muat_system_prompt(SYSTEM_PROMPT_PATH)
    return buat_rag_chain(retriever, model, system_prompt)


rag_chain = siapkan_chatbot()

# ============================================================
# 3B. DAFTAR CONTOH PERTANYAAN (dikelompokkan per jurnal)
# ============================================================

CONTOH_PERTANYAAN = {
    "Teknik Belajar Efektif": [
        "Apa itu active recall dan kenapa dianggap efektif?",
        "Apa yang dimaksud dengan spaced practice/distributed practice?",
    ],
    "Teknik Feynman untuk Slow Learners": [
        "Apa itu Teknik Feynman dan bagaimana langkah-langkahnya?",
        "Metode penelitian apa yang digunakan dalam studi Teknik Feynman ini?",
    ],
    "Illusion of Knowing": [
        "Apa yang dimaksud dengan illusion of knowing?",
        "Faktor apa saja yang memengaruhi illusion of knowing dalam metakognisi?",
    ],
}


# ============================================================
# 4. BUKU CATATAN PERCAKAPAN
# ============================================================
# st.session_state adalah tempat menyimpan data yang tidak ikut hilang
# saat file ini dijalankan ulang. Di sini dipakai untuk mencatat riwayat
# percakapan: siapa yang bicara ("user" atau "assistant") dan isinya.
# Sama saja dengan menjaga percakapan terus muncul di atas chat baru

if "riwayat" not in st.session_state:
    st.session_state.riwayat = []

if "pertanyaan_terpilih" not in st.session_state:
    st.session_state.pertanyaan_terpilih = None

# ============================================================
# 5. TAMPILAN
# ============================================================

with st.sidebar:

    _kolom_kiri, _kolom_logo, _kolom_kanan = st.columns([1, 1, 1])
    with open("assets/logo.png", "rb") as _f:
        _logo_base64 = base64.b64encode(_f.read()).decode()

    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom:0.5rem;">
            <img src="data:image/png;base64,{_logo_base64}" width="120">
            <div style="font-weight:800; font-size:1.5rem;">
                CogniLearn Chatbot
            </div>
            <div style="font-weight:600; font-size:0.9rem;">
                Mini Project 2 / PPKD AI Automation Engineer
            </div>
            <div style="font-weight:100; font-size:0.7rem;">
                Shergy Diardhan
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    st.header("Tentang chatbot ini")
    st.write(
        "Chatbot ini menganalisis tiga jurnal ilmiah untuk menjawab pertanyaan terkait metode belajar dan kesulitan pemahaman" \
        " dengan fokus pada Teknik Belajar Efektif, Teknik Feynman, dan Illusion of Knowing."
    )
    st.caption("Jawaban hanya diambil dari dokumen sumber, bukan dari internet.")
    if st.button("Mulai percakapan baru"):
        st.session_state.riwayat = []

    # --- Panel info sistem (statis, tidak perlu koneksi apa pun) ---
    \
    \
    st.subheader("Info sistem")
    st.markdown(
        f"""
        <div class="info-card"><b>Model:</b> {CHAT_MODEL_LABEL}</div>
        <div class="info-card"><b>Jumlah Dokumen Sumber:</b> {jumlah_dokumen_sumber}</div>
        <div class="info-card"><b>Mode:</b> Retrieval-Augmented Generation (RAG)</div>
        """,
        unsafe_allow_html=True,
    )

st.title("CogniLearn Chatbot — Asisten Metode Belajar")
st.caption("Tanyakan apa saja seputar Active Recall, Metode Feynman, dan Illusion of Knowing.")

# Salam pembuka, selalu tampil paling atas.
with st.chat_message("assistant"):
    st.markdown(
        "Halo, silakan ajukan pertanyaan."
    )

# Contoh pertanyaan, dikelompokkan per jurnal, ditampilkan sebagai
# tombol. Hanya muncul selagi percakapan masih kosong, supaya layar
# tidak penuh lagi begitu pengguna sudah mulai tanya jawab.
if not st.session_state.riwayat:
    st.markdown("**Belum tau mau tanya apa? Coba salah satu contoh di bawah ini:**")
    
    kolom = st.columns(len(CONTOH_PERTANYAAN))
    for kolom_ke, (nama_jurnal, daftar_pertanyaan) in zip(kolom, CONTOH_PERTANYAAN.items()):
        with kolom_ke:
            st.caption(nama_jurnal)
            for i, teks_pertanyaan in enumerate(daftar_pertanyaan):
                if st.button(
                    teks_pertanyaan,
                    key=f"contoh_{nama_jurnal}_{i}",
                    use_container_width=True,
                ):
                    st.session_state.pertanyaan_terpilih = teks_pertanyaan

# Tampilkan ulang seluruh riwayat percakapan dari buku catatan.
for pesan in st.session_state.riwayat:
    with st.chat_message(pesan["role"]):
        st.markdown(pesan["isi"])


# ============================================================
# 6. TANYA JAWAB
# ============================================================

pertanyaan = st.chat_input("Tulis pertanyaan Anda di sini...")

# Kalau pengguna mengklik salah satu tombol contoh pertanyaan (dan tidak
# sedang mengetik pertanyaan baru), pakai pertanyaan dari tombol itu.
if not pertanyaan and st.session_state.pertanyaan_terpilih:
    pertanyaan = st.session_state.pertanyaan_terpilih
    st.session_state.pertanyaan_terpilih = None

if pertanyaan:
    # Tampilkan pertanyaan, lalu catat ke buku catatan.
    with st.chat_message("user"):
        st.markdown(pertanyaan)
    st.session_state.riwayat.append({"role": "user", "isi": pertanyaan})

    # Minta jawaban ke mesin RAG. .stream() + st.write_stream() membuat
    # jawaban muncul bertahap, kata demi kata, seperti sedang diketik.
    with st.chat_message("assistant"):
        with st.spinner("Mencari jawaban di dokumen..."):
            jawaban = st.write_stream(rag_chain.stream(pertanyaan))
    st.session_state.riwayat.append({"role": "assistant", "isi": jawaban})