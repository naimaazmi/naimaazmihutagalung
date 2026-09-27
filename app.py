import streamlit as st
import os
import glob
from html import escape

# ----------------- KONFIGURASI HALAMAN -----------------
st.set_page_config(
    page_title="AI Tutor Bahasa Indonesia Naima H",
    page_icon="🌸",
    layout="wide"
)

# Folder tempat berkas materi disimpan
DATABASE_DIR = "database"

if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)

# ----------------- PEMBACAAN OTOMATIS & RELEVANSI MATERI -----------------
BANK_PERTANYAAN_TOPIK = {
    "sastra": "Bagaimana pendekatan struktural dan resepsi sastra dalam membedah karya sastra modern?",
    "apresiasi": "Apa langkah-langkah konkret dalam mengapresiasi dan menganalisis teks puisi serta prosa?",
    "dasar": "Jelaskan hakikat, fungsi, dan ragam kedudukan Bahasa Indonesia sebagai bahasa nasional!",
    "ejaan": "Bagaimana kaidah penggunaan tanda baca koma, titik dua, dan penulisan huruf kapital sesuai pedoman baku?",
    "keterampilan": "Bagaimana korelasi antara keterampilan menyimak kritis dengan kemampuan berbicara dialektis?",
    "morfologi": "Jelaskan perbedaan proses morfologis pembentukan afiksasi prefiks, infiks, sufiks, dan konfiks!",
    "semantik": "Bagaimana cara menganalisis pergeseran makna peyorasi, ameliorasi, dan konotatif dalam wacana?",
    "sintaksis": "Jelaskan fungsi sintaksis subjek, predikat, objek, dan pelengkap dalam kalimat majemuk bertingkat!",
    "wacana": "Bagaimana peranan kohesi gramatikal dan koherensi leksikal dalam menyusun paragraf wacana yang utuh?"
}

def muat_daftar_materi():
    """Membaca folder database secara dinamis."""
    berkas = sorted(glob.glob(os.path.join(DATABASE_DIR, "*.txt")))
    list_materi = []
    
    pilihan_ikon = ["📖", "✍️", "🎙️", "🧩", "📜", "🌐", "📐", "🎭", "💡", "📝", "📚", "🔍"]
    
    for idx, path in enumerate(berkas):
        nama_file = os.path.basename(path)
        nama_bersih = os.path.splitext(nama_file)[0].replace("_", " ").title()
        ikon = pilihan_ikon[idx % len(pilihan_ikon)]
        
        kata_kunci = os.path.splitext(nama_file)[0].lower()
        pertanyaan_cocok = None
        for kunci, tanya in BANK_PERTANYAAN_TOPIK.items():
            if kunci in kata_kunci:
                pertanyaan_cocok = tanya
                break
        if not pertanyaan_cocok:
            pertanyaan_cocok = f"Jelaskan prinsip dasar, teori, dan contoh implementasi mengenai {nama_bersih}!"
        
        list_materi.append({
            "path": path,
            "nama": nama_bersih,
            "ikon": ikon,
            "contoh_tanya": pertanyaan_cocok
        })
    return list_materi

def ambil_konten(filepath):
    """Membaca isi berkas materi."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                konten = f.read().strip()
                return konten if konten else "Materi pada berkas ini masih kosong."
        except Exception as e:
            return f"Terjadi kendala saat membaca materi: {e}"
    return "Berkas materi tidak ditemukan."

def cari_jawaban_di_database(pertanyaan, daftar_materi):
    """Mencari isi materi yang paling relevan berdasarkan pertanyaan pengguna."""
    if not daftar_materi:
        return "Belum ada berkas materi di folder database."

    pertanyaan_lower = pertanyaan.lower()
    
    stop_words = {"adalah", "yang", "dan", "atau", "dari", "pada", "untuk", "dengan", "apa", "itu", "bagaimana", "mengapa"}
    kata_kunci_list = [k for k in pertanyaan_lower.split() if len(k) > 2 and k not in stop_words]

    if not kata_kunci_list:
        kata_kunci_list = [k for k in pertanyaan_lower.split() if len(k) > 2]

    materi_terkait = []

    for materi in daftar_materi:
        nama_materi = materi["nama"].lower()
        konten = ambil_konten(materi["path"])
        konten_lower = konten.lower()

        skor = 0
        for kata in kata_kunci_list:
            if kata in nama_materi:
                skor += 5
            if kata in konten_lower:
                skor += 1

        if skor > 0:
            materi_terkait.append((skor, materi["nama"], konten))

    materi_terkait.sort(key=lambda x: x[0], reverse=True)

    if materi_terkait:
        materi_terbaik = materi_terkait[0]
        return f"📌 **Materi Terkait: {materi_terbaik[1]}**\n\n{materi_terbaik[2]}"
    else:
        m1 = daftar_materi[0]
        isi1 = ambil_konten(m1["path"])
        return f"Sistem tidak menemukan kata kunci yang spesifik. Berikut referensi dari materi **{m1['nama']}**:\n\n{isi1}"

# ----------------- PERTANYAAN & PANDUAN DINAMIS -----------------
def buat_pertanyaan_kerap_muncul(daftar_materi):
    """Membuat 3 pertanyaan yang mengikuti materi di folder database."""
    pertanyaan = []

    for materi in daftar_materi[:3]:
        nama = escape(materi["nama"])
        pertanyaan.append(f"Apa konsep utama yang perlu dipahami dalam materi {nama}?")

    return pertanyaan[:3]

def buat_panduan_bertanya(daftar_materi):
    """Menyusun panduan berdasarkan materi yang tersedia."""
    if not daftar_materi:
        return [
            "Tambahkan berkas materi berformat .txt ke folder database.",
            "Gunakan pertanyaan yang jelas dan sebutkan topik yang ingin dipelajari."
        ]

    nama_materi = ", ".join(
        escape(m["nama"]) for m in daftar_materi[:3]
    )

    panduan = [
        f"Gunakan nama materi secara spesifik, misalnya: {nama_materi}.",
        "Tanyakan satu konsep utama dalam satu pertanyaan agar jawaban lebih terarah.",
        "Tambahkan permintaan contoh, perbandingan, langkah analisis, atau rangkuman sesuai kebutuhan.",
    ]

    if len(daftar_materi) > 3:
        panduan.append(
            f"Database memuat {len(daftar_materi)} materi; pilih topik yang paling sesuai dari daftar materi."
        )

    return panduan

# Muat data materi aktif
materi_aktif = muat_daftar_materi()
total_materi = len(materi_aktif)

# Inisialisasi state interaksi
if "teks_pertanyaan" not in st.session_state:
    st.session_state.teks_pertanyaan = ""
if "jawaban_tutor" not in st.session_state:
    st.session_state.jawaban_tutor = None
if "tampilkan_daftar_materi" not in st.session_state:
    st.session_state.tampilkan_daftar_materi = False

# Callback khusus untuk membersihkan halaman
def bersihkan_halaman():
    st.session_state.teks_pertanyaan = ""
    st.session_state.jawaban_tutor = None

# ----------------- CSS RESPONSIF & PENGATURAN TATA LETAK -----------------
st.markdown("""
<style>
    /* MEMBERIKAN JARAK AMAN DARI HEADER ATAS */
    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 2rem !important;
    }

    /* 1. TAMPILAN UMUM & DESKTOP */
    html, body, .stApp, .stApp p, .stApp div, .stApp span, .stApp label,
    .stApp button, .stApp textarea, .stApp input, .stApp h1, .stApp h2,
    .stApp h3, .stApp h4, .stApp li {
        font-family: 'Times New Roman', Times, serif !important;
        text-align: center;
    }

    .stApp {
        background-color: #fdf2f6;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(255, 255, 255, 0.75) 0%, transparent 45%),
            radial-gradient(circle at 90% 85%, rgba(252, 228, 236, 0.8) 0%, transparent 45%),
            url("data:image/svg+xml,%3Csvg width='180' height='180' viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' stroke='%23f06292' stroke-width='0.9' stroke-opacity='0.22'%3E%3Cpath d='M90,30 C75,5 40,15 45,45 C15,40 10,75 35,90 C15,115 45,145 70,125 C85,155 120,145 115,115 C145,120 155,85 130,70 C150,40 120,15 90,30 Z'/%3E%3Cpath d='M90,48 C80,30 55,38 58,60 C38,58 35,82 52,92 C38,110 60,130 78,118 C88,138 112,130 110,110 C130,112 138,88 120,78 C132,58 110,38 90,48 Z'/%3E%3Ccircle cx='90' cy='85' r='6' stroke='%23ad1457' stroke-opacity='0.3'/%3E%3Cpath d='M90,91 Q90,145 60,170' stroke='%23ec407a' stroke-opacity='0.25' stroke-linecap='round'/%3E%3Cpath d='M88,115 Q120,110 135,128 C135,128 118,138 90,125' stroke='%23f48fb1' stroke-opacity='0.22'/%3E%3Cpath d='M75,138 Q45,135 35,152 C35,152 55,156 70,145' stroke='%23f48fb1' stroke-opacity='0.22'/%3E%3Cpath d='M15,20 Q30,10 40,30' stroke='%23f48fb1' stroke-opacity='0.18'/%3E%3Cpath d='M160,15 Q145,30 165,45' stroke='%23f48fb1' stroke-opacity='0.18'/%3E%3C/g%3E%3C/svg%3E");
        background-repeat: repeat;
        background-attachment: fixed;
        color: #3b1f2b;
    }

    .main-wrapper {
        max-width: 900px;
        margin: 0 auto;
        padding-bottom: 50px;
        text-align: center;
    }

    .greeting-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #f8bbd0;
        padding: 6px 20px;
        border-radius: 25px;
        font-size: 0.92rem;
        color: #ad1457;
        font-style: italic;
        margin: 0 auto 15px auto;
        box-shadow: 0 4px 12px rgba(244, 143, 177, 0.2);
        white-space: nowrap;
        max-width: 100%;
    }

    .hero-banner {
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(8px);
        border: 2px solid #f48fb1;
        border-radius: 24px;
        padding: 24px 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 15px;
        box-shadow: 0 10px 25px rgba(233, 30, 99, 0.08);
        margin-bottom: 25px;
        text-align: center !important;
        width: 100%;
    }

    .hero-banner > div {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .hero-icon {
        flex-shrink: 0;
        width: 90px;
        height: 90px;
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #880e4f;
        line-height: 1.2;
        margin: 0 auto 10px auto;
        text-align: center !important;
        width: 100% !important;
        text-wrap: balance; /* Memastikan pemotongan teks seimbang kanan-kiri */
        display: block;
    }

    .main-desc {
        font-size: 1.05rem;
        line-height: 1.55;
        color: #5c3543;
        margin: 0 auto;
        text-align: center !important;
        width: 100%;
    }

    .tag-wrapper {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 8px;
        margin-top: 14px;
        width: 100%;
    }

    .tag-item {
        background: #fce4ec;
        border: 1px solid #f48fb1;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: bold;
        color: #ad1457;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.9);
        border: 1.5px solid #f8bbd0;
        border-radius: 18px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(240, 98, 146, 0.08);
        height: 100%;
    }

    .metric-num {
        font-size: 1.35rem;
        font-weight: bold;
        color: #9c2748;
        margin: 0;
        text-align: center;
    }

    .metric-info {
        font-size: 0.92rem;
        color: #6a3e50;
        margin: 4px 0 0 0;
        text-align: center;
    }

    .section-headline {
        font-size: 1.85rem;
        font-weight: bold;
        color: #7b113a;
        margin-top: 35px;
        margin-bottom: 4px;
        text-align: center !important;
    }

    .section-subtext {
        font-size: 1rem;
        color: #6a4050;
        text-align: center !important;
        margin-bottom: 22px;
        font-style: italic;
    }

    .card-info {
        background: rgba(255, 255, 255, 0.92);
        border: 1.5px solid #f48fb1;
        border-top: 5px solid #ad1457;
        border-radius: 16px;
        padding: 18px 22px;
        margin-bottom: 14px;
        box-shadow: 0 4px 14px rgba(244, 143, 177, 0.12);
        text-align: center !important;
    }

    .card-info-title {
        font-size: 1.15rem;
        font-weight: bold;
        color: #880e4f;
        margin-bottom: 6px;
        text-align: center !important;
    }

    .card-info-desc {
        font-size: 0.98rem;
        color: #4a2534;
        margin: 0;
        line-height: 1.6;
        text-align: center !important;
    }

    .card-info-left {
        background: rgba(255, 255, 255, 0.92);
        border: 1.5px solid #f48fb1;
        border-top: 5px solid #ad1457;
        border-radius: 16px;
        padding: 18px 22px;
        margin-bottom: 14px;
        box-shadow: 0 4px 14px rgba(244, 143, 177, 0.12);
        text-align: left !important;
    }

    .card-info-left .card-info-title {
        font-size: 1.15rem;
        font-weight: bold;
        color: #880e4f;
        margin-bottom: 8px;
        text-align: left !important;
    }

    .card-info-left .card-info-desc {
        font-size: 0.98rem;
        color: #4a2534;
        margin: 0;
        line-height: 1.6;
        text-align: left !important;
    }

    .stTextArea textarea {
        background-color: #ffffff !important;
        border: 2px solid #f48fb1 !important;
        border-radius: 18px !important;
        padding: 16px !important;
        font-size: 1.05rem !important;
        color: #2b1720 !important;
        text-align: center !important;
        box-shadow: 0 4px 15px rgba(244, 143, 177, 0.18) !important;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #a63a58 0%, #7d1c37 100%) !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 10px 20px !important;
        width: 100% !important;
        box-shadow: 0 6px 16px rgba(125, 28, 55, 0.3) !important;
        transition: all 0.25s ease !important;
        text-align: center !important;
        text-transform: uppercase !important;
        white-space: pre-line !important;
        line-height: 1.35 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    .topic-card {
        min-height: 78px;
        height: auto;
        box-sizing: border-box;
        background: rgba(255, 255, 255, 0.95);
        border: 1.5px solid #f8bbd0;
        border-radius: 18px;
        padding: 15px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .topic-name {
        font-size: 1.15rem;
        font-weight: bold;
        color: #880e4f;
        text-align: center;
    }

    /* 2. PENYESUAIAN KHUSUS HP (< 768px) */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 3rem !important;
        }

        .main-wrapper {
            padding-bottom: 25px;
        }

        .greeting-pill {
            font-size: 0.72rem !important;
            padding: 4px 12px !important;
            gap: 4px !important;
            margin-bottom: 12px;
        }

        .hero-banner {
            padding: 16px 12px;
            gap: 12px;
            border-radius: 16px;
        }

        .hero-icon {
            width: 70px !important;
            height: 70px !important;
        }

        .main-title {
            font-size: 1.45rem !important;
            line-height: 1.3 !important;
            margin: 0 auto 6px auto !important;
            text-align: center !important;
            width: 100% !important;
            text-wrap: balance !important; /* Menjamin judul rata tengah seimbang di HP */
        }

        .main-desc {
            font-size: 0.88rem !important;
            line-height: 1.45;
            text-align: center !important;
        }

        .tag-wrapper {
            gap: 5px;
            margin-top: 10px;
        }

        .tag-item {
            font-size: 0.72rem;
            padding: 2px 8px;
        }

        .metric-card {
            padding: 10px;
            margin-bottom: 6px;
        }

        .metric-num {
            font-size: 1rem !important;
        }

        .metric-info {
            font-size: 0.78rem !important;
        }

        .section-headline {
            font-size: 1.1rem !important;
            margin-top: 22px;
            white-space: nowrap;
        }

        .section-subtext {
            font-size: 0.85rem !important;
            margin-bottom: 14px;
        }

        .card-info, .card-info-left {
            padding: 12px 14px !important;
            border-radius: 12px !important;
            margin-bottom: 10px !important;
        }

        .card-info-title, .card-info-left .card-info-title {
            font-size: 0.98rem !important;
        }

        .card-info-desc, .card-info-left .card-info-desc {
            font-size: 0.85rem !important;
            line-height: 1.4;
        }

        .stTextArea textarea {
            font-size: 0.92rem !important;
            padding: 10px !important;
            border-radius: 12px !important;
        }

        div.stButton > button {
            font-size: 0.85rem !important;
            padding: 8px 12px !important;
            border-radius: 20px !important;
        }

        .topic-card {
            min-height: 55px;
            padding: 10px;
            border-radius: 12px;
        }

        .topic-name {
            font-size: 0.95rem;
        }
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

# ----------------- 1. HEADER UTAMA -----------------
st.markdown("""
<div class="greeting-pill">
    🌸 Selamat Datang • Mari Mengasah Bahasa Bersama Hari Ini 🌸
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-icon">
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="pinkHead" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#ff80ab;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#f06292;stop-opacity:1" />
                </linearGradient>
                <linearGradient id="bodyG" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#fce4ec;stop-opacity:1" />
                </linearGradient>
            </defs>
            <circle cx="50" cy="11" r="5.5" fill="#ec407a" />
            <path d="M50 16 L50 24" stroke="#ec407a" stroke-width="3" stroke-linecap="round"/>
            <rect x="22" y="24" width="56" height="42" rx="18" fill="url(#pinkHead)"/>
            <rect x="28" y="30" width="44" height="30" rx="10" fill="#2d132c"/>
            <circle cx="40" cy="45" r="4.5" fill="#ff4081" />
            <circle cx="60" cy="45" r="4.5" fill="#ff4081" />
            <circle cx="41.5" cy="43.5" r="1.5" fill="#ffffff" />
            <circle cx="61.5" cy="43.5" r="1.5" fill="#ffffff" />
            <ellipse cx="34" cy="51" rx="3.5" ry="1.8" fill="#f48fb1"/>
            <ellipse cx="66" cy="51" rx="3.5" ry="1.8" fill="#f48fb1"/>
            <path d="M47 51 Q50 54 53 51" stroke="#ff80ab" stroke-width="1.8" fill="none" stroke-linecap="round"/>
            <rect x="15" y="37" width="7" height="16" rx="3" fill="#f48fb1"/>
            <rect x="78" y="37" width="7" height="16" rx="3" fill="#f48fb1"/>
            <rect x="33" y="69" width="34" height="25" rx="10" fill="url(#bodyG)" stroke="#f8bbd0" stroke-width="2"/>
            <circle cx="50" cy="80" r="4.5" fill="#ec407a"/>
            <rect x="20" y="71" width="10" height="16" rx="5" fill="#f8bbd0" />
            <rect x="70" y="71" width="10" height="16" rx="5" fill="#f8bbd0" />
        </svg>
    </div>
    <div>
        <h1 class="main-title">AI Tutor Bahasa Indonesia Naima H</h1>
        <p class="main-desc">
            Mendalami seluk-beluk kaidah Bahasa Indonesia kini terasa lebih ringan, terstruktur, serta komunikatif. 
            Terhubung otomatis dengan seluruh arsip kebahasaan Anda yang tersimpan di dalam basis data.
        </p>
        <div class="tag-wrapper">
            <span class="tag-item">📚 {total_materi} Rumpun Materi</span>
            <span class="tag-item">🎯 Sinkron Otomatis</span>
            <span class="tag-item">🤖 Asisten Interaktif</span>
            <span class="tag-item">🧠 AI Cerdas</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- 2. METRIK TIGA KOLOM -----------------
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-num">📖 {total_materi} Materi</div>
        <div class="metric-info">Siap dipelajari dan dianalisis.</div>
    </div>
    """, unsafe_allow_html=True)
with col_m2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-num">💭 Konsultasi</div>
        <div class="metric-info">Eksplorasi tata bahasa & sastra.</div>
    </div>
    """, unsafe_allow_html=True)
with col_m3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-num">🔍 Cerdas</div>
        <div class="metric-info">Otomatis sinkron dengan arsip.</div>
    </div>
    """, unsafe_allow_html=True)

# ----------------- 3. DAFTAR MATERI OTOMATIS -----------------
st.markdown('<div class="section-headline">❧ Pustaka Materi Pembelajaran ☙</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtext">Klik bagian di bawah untuk melihat materi yang tersedia:</div>',
    unsafe_allow_html=True
)

if not materi_aktif:
    st.info("Belum ada materi di basis data. Silakan simpan berkas .txt baru di folder database.")
else:
    label_daftar = (
        f"📚 SEMBUNYIKAN DAFTAR MATERI 📚\n({total_materi} MATERI TERSEDIA)"
        if st.session_state.tampilkan_daftar_materi
        else f"📚 LIHAT DAFTAR MATERI 📚\n({total_materi} MATERI TERSEDIA)"
    )

    if st.button(label_daftar, use_container_width=True, key="toggle_daftar_materi"):
        st.session_state.tampilkan_daftar_materi = (
            not st.session_state.tampilkan_daftar_materi
        )
        st.rerun()

    if st.session_state.tampilkan_daftar_materi:
        st.markdown(
            '<p style="color:#6a4050; margin: 10px 0 15px 0; font-style: italic; text-align: center;">'
            'Pilih salah satu materi untuk membuka isi dan contoh pertanyaannya.'
            '</p>',
            unsafe_allow_html=True
        )

        for i in range(0, len(materi_aktif), 2):
            c1, c2 = st.columns(2)

            m1 = materi_aktif[i]
            with c1:
                st.markdown(
                    f'<div class="topic-card">'
                    f'<div class="topic-name">{m1["ikon"]} {m1["nama"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if st.button(
                    f"📖 Pelajari {m1['nama']}",
                    key=f"btn_{i}_{m1['nama']}",
                    use_container_width=True
                ):
                    st.session_state.teks_pertanyaan = m1["contoh_tanya"]
                    st.session_state.jawaban_tutor = ambil_konten(m1["path"])
                    st.rerun()

            if i + 1 < len(materi_aktif):
                m2 = materi_aktif[i + 1]
                with c2:
                    st.markdown(
                        f'<div class="topic-card">'
                        f'<div class="topic-name">{m2["ikon"]} {m2["nama"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    if st.button(
                        f"📖 Pelajari {m2['nama']}",
                        key=f"btn_{i+1}_{m2['nama']}",
                        use_container_width=True
                    ):
                        st.session_state.teks_pertanyaan = m2["contoh_tanya"]
                        st.session_state.jawaban_tutor = ambil_konten(m2["path"])
                        st.rerun()

# ----------------- 4. INFORMASI DINAMIS -----------------
pertanyaan_kerap = buat_pertanyaan_kerap_muncul(materi_aktif)
panduan_bertanya = buat_panduan_bertanya(materi_aktif)

faq_html = "<br>".join(f"• {q}" for q in pertanyaan_kerap)
if not faq_html:
    faq_html = "Belum ada pertanyaan yang dapat dibuat. Tambahkan materi ke folder database."

st.markdown(f"""
<div class="card-info-left" style="margin-top:20px;">
    <div class="card-info-title">Pertanyaan yang Kerap Muncul</div>
    <div class="card-info-desc">{faq_html}</div>
</div>
""", unsafe_allow_html=True)

panduan_html = "<br>".join(f"• {p}" for p in panduan_bertanya)
st.markdown(f"""
<div class="card-info-left">
    <div class="card-info-title">Panduan Bertanya Efektif</div>
    <div class="card-info-desc">{panduan_html}</div>
</div>
""", unsafe_allow_html=True)

# ----------------- 5. FORMULIR TANYA JAWAB UTAMA -----------------
st.markdown("""
<div class="card-info" style="margin-top: 20px; border-top-color: #7b113a;">
    <div class="card-info-title">💬 Ajukan Pertanyaan kepada AI Tutor</div>
    <div class="card-info-desc">
        Tuliskan konsep atau pertanyaan kebahasaan Anda. AI Tutor Naima H akan menelusuri data materi yang bersesuaian.
    </div>
</div>
""", unsafe_allow_html=True)

pertanyaan_user = st.text_area(
    label="Kotak Pertanyaan",
    key="teks_pertanyaan",
    placeholder="Ketik pertanyaan atau konsep kebahasaan yang ingin Anda pelajari...",
    height=100,
    label_visibility="collapsed"
)

# TATA LETAK TOMBOL RATA TENGAH
_, col_aksi1, col_aksi2, _ = st.columns([0.5, 2.5, 2.5, 0.5])

with col_aksi1:
    if st.button("➤ AJUKAN SEKARANG", use_container_width=True):
        if st.session_state.teks_pertanyaan.strip():
            with st.spinner("🌸 AI Tutor Naima H sedang menelaah basis data materi Anda..."):
                st.session_state.jawaban_tutor = cari_jawaban_di_database(st.session_state.teks_pertanyaan, materi_aktif)
        else:
            st.warning("Silakan tuliskan pertanyaan terlebih dahulu ya! 💕")

with col_aksi2:
    st.button("🔄 BERSIHKAN", on_click=bersihkan_halaman, use_container_width=True)

# Kotak Hasil Jawaban / Isi Berkas
if st.session_state.jawaban_tutor:
    st.markdown("""
    <div class="card-info" style="background:#fffafc; border-top-color:#2e7d32; margin-top:20px;">
        <div class="card-info-title" style="color:#2e7d32;">📖 Uraian Materi / Jawaban Tutor Naima H</div>
    </div>
    """, unsafe_allow_html=True)
    st.info(st.session_state.jawaban_tutor)

# ----------------- 6. PENUTUP -----------------
st.markdown("""
<div class="card-info" style="margin-top: 25px; background: #fae4ec; border: 1.5px dashed #ad1457; text-align: center;">
    <div class="card-info-title">🌸 Terus Asah Kemampuan Bahasa Bersama AI Tutor Naima H 🌸</div>
    <div class="card-info-desc">
        “Belajar menjadi lebih bermakna ketika setiap materi membuka ruang untuk bertanya, memahami, dan berkembang.”
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
