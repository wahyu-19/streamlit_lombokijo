import streamlit as st
import matplotlib.pyplot as plt
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
        padding: 2rem 3rem 2rem 3rem !important; /* padding atas, kanan, bawah, kiri */
    }

    .big-title {
        font-size: 56px;
        font-weight: 900;
        margin-bottom: 0.5rem;
        color: #111;
        margin-top: 0px;
    }

    .description {
        font-size: 22px;
        color: #333;
        margin-bottom: 2rem;
    }

    .metric-box {
        background-color: white;
        width: 100%;
        max-width: 320px;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 16px;
        color: #4CD964;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 1.2rem;
        box-shadow: 0 0 10px rgba(76, 217, 100, 0.3);
        padding: 1rem;
        margin-left: auto;
        margin-right: auto;
    }

    .icon {
        font-size: 32px;
        margin-right: 10px;
        vertical-align: middle;
    }

    /* Responsif untuk layar kecil (HP) */
    @media screen and (max-width: 768px) {
        .big-title {
            font-size: 42px;
            text-align: center;
        }
        .description {
            font-size: 18px;
            text-align: center;
        }
        .metric-box {
            max-width: 100%;
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
    st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><div class="icon">🌡️</div>{suhu}°C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><div class="icon">💧</div>{kelembapan}%</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><div class="icon">☀️</div>{uv_now}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
