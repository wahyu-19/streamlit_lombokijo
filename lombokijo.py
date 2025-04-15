import streamlit as st
import requests
import os
from streamlit_autorefresh import st_autorefresh

# ----------------------------
# HARUS PALING ATAS: Konfigurasi halaman
# ----------------------------
st.set_page_config(
    page_title="Blow n Glow",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------
# Auto-refresh setiap 10 detik
# ----------------------------
st_autorefresh(interval=10_000, key="refresh")

# ----------------------------
# Styling kustom
# ----------------------------
st.markdown("""
    <style>
    body, .main, .block-container {
        background-color: white !important;
        padding: 2vw;  /* Memberikan padding kiri-kanan-atas-bawah responsif */
    }

    .big-title {
        font-size: 6vw;  /* Menyesuaikan ukuran font dengan lebar layar */
        font-weight: 900;
        margin-bottom: 1.5rem;
        color: #111;
        margin-top: -40px;
        text-align: center;
    }

    .description {
        font-size: 3vw;
        color: #333;
        margin-top: -10px;
        margin-bottom: 1.5rem;
        text-align: center;
    }

    .metric-box {
        background-color: white;
        width: 90%;
        max-width: 400px;  /* Mengatur ukuran maksimal agar tidak terlalu besar */
        height: 100px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-radius: 16px;
        color: #4CD964;
        font-size: 5vw;  /* Ukuran font mengikuti layar */
        font-weight: 700;
        margin-bottom: 1rem;
        box-shadow: 0 0 10px rgba(76, 217, 100, 0.4);
        border: none;
        margin-left: auto;
        margin-right: auto;
    }

    .icon {
        font-size: 6vw;
        margin-right: 10px;
        vertical-align: middle;
    }

    /* Responsif untuk layar kecil (HP) */
    @media screen and (max-width: 768px) {
        .big-title {
            font-size: 8vw;  /* Menyesuaikan ukuran font pada layar kecil */
        }
        .description {
            font-size: 4vw;
        }
        .metric-box {
            max-width: 90%;  /* Menyesuaikan ukuran box pada layar kecil */
        }
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Konfigurasi Ubidots
# ----------------------------
UBIDOTS_ENDPOINT = "http://industrial.api.ubidots.com/api/v1.6/devices/esp32/"
header_ubidots = {
    "Content-Type": "application/json",
    "X-Auth-Token": "BBUS-GoISeXoa4YzzhmEgmoKUVgiv2Y3n9H"
}

# ----------------------------
# Fungsi Ambil Data
# ----------------------------
def get_variable_value(variable):
    try:
        url = f"{UBIDOTS_ENDPOINT}{variable}/lv"
        response = requests.get(url, headers=header_ubidots)
        if response.status_code == 200:
            return float(response.text)
        else:
            return "N/A"
    except Exception as e:
        print("❌ Ubidots Error:", e)
        return "N/A"

# ----------------------------
# Ambil data dari Ubidots
# ----------------------------
suhu = get_variable_value("temperature")
kelembapan = get_variable_value("humidity")
uv_now = get_variable_value("uv")  # Langsung ambil nilai terakhir

# ----------------------------
# Layout: 2 kolom besar (6:4)
# ----------------------------
col_left, col_right = st.columns([6, 4])

# ----------------------------
# Kolom KIRI: Judul, Deskripsi, Gambar
# ----------------------------
with col_left:
    st.markdown('<div class="big-title">Blow n Glow</div>', unsafe_allow_html=True)
    st.markdown('<div class="description">Know when to reapply your sunscreen — and don\'t forget to care for the Earth while you\'re at it.</div>', unsafe_allow_html=True)

    image_path = ""

    if isinstance(uv_now, (int, float)):
        if uv_now <= 2:
            image_path = "Sejuk.png"
        elif 3 <= uv_now <= 5:
            image_path = "sedang.png"
        else:
            image_path = "panas banget.png"
    else:
        image_path = "Sejuk.png"

    if os.path.exists(image_path):
        st.image(image_path, width=500)
    else:
        st.warning("⚠️ Gambar tidak ditemukan!")

# ----------------------------
# Kolom KANAN: Metrik
# ----------------------------
with col_right:
    st.markdown(f'<div class="metric-box"><span class="icon">🌡️</span>{suhu}°C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><span class="icon">💧</span>{kelembapan}%</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><span class="icon">☀️</span>{uv_now}</div>', unsafe_allow_html=True)
