import streamlit as st
import requests
import os
from streamlit_autorefresh import st_autorefresh

# ----------------------------
# Konfigurasi halaman
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
# Styling kustom (CSS)
# ----------------------------
st.markdown("""
    <style>
    body, .main, .block-container {
        background-color: white !important;
        padding: 2rem 3rem 2rem 3rem !important;
    }

    .container-flex {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }

    .left-content {
        flex: 1;
        min-width: 300px;
    }

    .right-content {
        flex: 1;
        min-width: 300px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
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
        max-width: 300px;
        height: 90px;
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
    }

    .icon {
        font-size: 28px;
        margin-right: 10px;
        vertical-align: middle;
    }

    img {
        max-width: 100%;
        height: auto;
    }

    @media screen and (max-width: 768px) {
        .container-flex {
            flex-direction: column;
            align-items: center;
        }

        .big-title {
            font-size: 42px;
            text-align: center;
        }

        .description {
            font-size: 18px;
            text-align: center;
        }

        .metric-box {
            max-width: 90%;
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
uv_now = get_variable_value("uv")

# ----------------------------
# Layout Flex
# ----------------------------
st.markdown('<div class="container-flex">', unsafe_allow_html=True)

# KIRI
st.markdown('<div class="left-content">', unsafe_allow_html=True)
st.markdown('<div class="big-title">Blow n Glow</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Know when to reapply your sunscreen — and don\'t forget to care for the Earth while you\'re at it.</div>', unsafe_allow_html=True)

# Tentukan gambar UV
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

# Tampilkan gambar
if os.path.exists(image_path):
    st.image(image_path, use_column_width=True)
else:
    st.warning("⚠️ Gambar tidak ditemukan!")
st.markdown('</div>', unsafe_allow_html=True)

# KANAN
st.markdown('<div class="right-content">', unsafe_allow_html=True)
st.markdown(f'<div class="metric-box"><span class="icon">🌡️</span>{suhu}°C</div>', unsafe_allow_html=True)
st.markdown(f'<div class="metric-box"><span class="icon">💧</span>{kelembapan}%</div>', unsafe_allow_html=True)
st.markdown(f'<div class="metric-box"><span class="icon">☀️</span>{uv_now}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Tutup container-flex
